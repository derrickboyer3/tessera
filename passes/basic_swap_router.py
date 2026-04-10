'''
    Basic Swap Router
    -----------------
    A transpiler pass that routes a layout-mapped circuit to be compatible with the
    physical connectivity constraints of the target hardware. It does this in two steps:

    Step 1 — Layout Application:
        Rewrites all instruction qubit indices from logical qubits to physical qubits
        using the layout stored in circuit.layout. This step requires a layout pass
        (TrivialPass or DenseLayoutPass) to have been run beforehand.

    Step 2 — Swap Insertion:
        Iterates through every instruction and checks if two-qubit gates are between
        physically adjacent qubits on the coupling map. If not, SWAP gates are inserted
        along the shortest path to bring the qubits adjacent before the gate runs.
        Qubit positions are tracked and updated as SWAPs move logical qubits to new
        physical locations.

    Single qubit gates and measurements are passed through unchanged.
    Gates with more than 2 qubits raise a ValueError — run BasisTranslationPass first
    to decompose them into 2-qubit gates before routing.

    Uses BFS (Breadth First Search) by default to find the shortest path between
    non-adjacent qubits. A custom path-finding strategy can be injected via the
    optional path_finder parameter in the constructor, allowing alternative routing
    algorithms to be swapped in without modifying this class.

    Args:
        coupling_map: The TesseraCouplingMap representing hardware connectivity
        path_finder: Optional callable(start, end) -> list[int] for custom routing.
                     Defaults to built-in BFS implementation.

    Raises:
        ValueError: If no layout is found on the circuit.
        ValueError: If a gate with more than 2 qubits is encountered.
'''
from circuit import TesseraCircuit
from hardware.coupling_map import TesseraCouplingMap
from transpiler_pass import TranspilerPass
from instruction import TesseraInstruction

class BasicSwapRouter(TranspilerPass):
    def __init__(self, coupling_map: TesseraCouplingMap, path_finder=None):
        self.coupling_map = coupling_map
        self.path_finder = path_finder if path_finder is not None else self.bfs_path

    def bfs_path(self, start, end):
        if start == end:
            return [start]
        
        visited = {start}
        queue = [[start]]  # queue of paths, not just nodes
        
        while queue:
            path = queue.pop(0)
            current = path[-1]
            
            for neighbor in self.coupling_map.neighbors(current):
                if neighbor == end:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        
        raise ValueError(f"Tessera: No path exists between q{start} and q{end} in the coupling map")

    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        # Step 0: Set Up
        layout = circuit.layout
        if not layout:
            raise ValueError("Tessera: No layout found on circuit. Run a layout pass before BasicSwapRouter.")

        # Step 1: Apply Layout
        remapped_ins = []
        for ins in circuit.instructions:
            remapped_qubits = [layout[q] for q in ins.qubits]
            remapped_ins.append(TesseraInstruction(ins.name, remapped_qubits, ins.clbits, ins.params))

        # Step 2: Iterate instructions and insert swap gates where needed
        current_positions = dict(layout)
        inverse_positions = {v: k for k, v in layout.items()}
        swapped_remapped_ins = []
        for ins in remapped_ins:
            # Handle single qubit + measure gates
            if ins.name in ("measure", "barrier"):
                swapped_remapped_ins.append(ins)
                continue
            if len(ins.qubits) == 1:
                swapped_remapped_ins.append(ins)
                continue

            # Handle multi-qubit gates
            if len(ins.qubits) == 2:
                p0, p1 = ins.qubits[0], ins.qubits[1]
                if self.coupling_map.are_connected(p0, p1):
                    # Already adjacent, just keep the gate
                    swapped_remapped_ins.append(ins)
                else:
                    # Not adjacent, need to insert SWAPs
                    path = self.path_finder(p0, p1)
                    # path is like [p0, p1, p2, p3]
                    # insert swaps along the path to bring p0 next to p1
                    for i in range(len(path) - 2):
                        swap_a = path[i]
                        swap_b = path[i + 1]
                        swapped_remapped_ins.append(TesseraInstruction("swap", [swap_a, swap_b], [], []))
                        # Update tracking dicts
                        log_a = inverse_positions[swap_a]
                        log_b = inverse_positions[swap_b]
                        current_positions[log_a], current_positions[log_b] = swap_b, swap_a
                        inverse_positions[swap_a], inverse_positions[swap_b] = log_b, log_a
                    # Now p0 is adjacent to p1, append the gate with updated position
                    swapped_remapped_ins.append(TesseraInstruction(ins.name, [path[-2], path[-1]], ins.clbits, ins.params))
            elif len(ins.qubits) > 2:
                raise ValueError(f"Tessera: BasicSwapRouter encountered a {len(ins.qubits)}-qubit gate '{ins.name}'. Decompose to 2-qubit gates first using BasisTranslationPass.")
        
        return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, swapped_remapped_ins, layout)