'''
    Basic Swap Router
    -----------------
    A transpiler pass that routes a layout-mapped circuit to be compatible with the
    physical connectivity constraints of the target hardware.

    Algorithm:
        Walks the circuit instruction by instruction. For each instruction it
        translates the logical qubit indices into physical qubits using the
        current logical-to-physical mapping (which starts equal to circuit.layout
        and is updated whenever a SWAP is inserted). For two-qubit gates whose
        translated physical qubits are not adjacent on the coupling map, SWAP
        gates are inserted along the shortest path to bring them adjacent before
        the gate runs, and the mapping is updated accordingly so that all
        subsequent instructions reference the correct physical qubits.

    Single qubit gates, measurements, and barriers are emitted with their qubit
    indices translated to the current physical mapping.

    Gates with more than 2 qubits raise a ValueError — run BasisTranslationPass
    first to decompose them into 2-qubit gates before routing.

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

        # current_positions and inverse_positions start equal to the initial layout
        # and are updated each time a SWAP moves a logical qubit. Subsequent
        # instructions are translated using current_positions so they land on the
        # right physical qubits after any SWAPs have shifted things around.
        current_positions = dict(layout)
        inverse_positions = {v: k for k, v in layout.items()}

        out = []
        for ins in circuit.instructions:
            physical_qubits = [current_positions[q] for q in ins.qubits]

            if ins.name in ("measure", "barrier"):
                out.append(TesseraInstruction(ins.name, physical_qubits, ins.clbits, ins.params))
                continue
            if len(ins.qubits) == 1:
                out.append(TesseraInstruction(ins.name, physical_qubits, ins.clbits, ins.params))
                continue

            if len(ins.qubits) == 2:
                p0, p1 = physical_qubits[0], physical_qubits[1]
                if self.coupling_map.are_connected(p0, p1):
                    out.append(TesseraInstruction(ins.name, [p0, p1], ins.clbits, ins.params))
                else:
                    path = self.path_finder(p0, p1)
                    for i in range(len(path) - 2):
                        swap_a = path[i]
                        swap_b = path[i + 1]
                        out.append(TesseraInstruction("swap", [swap_a, swap_b], [], []))
                        log_a = inverse_positions[swap_a]
                        log_b = inverse_positions[swap_b]
                        current_positions[log_a], current_positions[log_b] = swap_b, swap_a
                        inverse_positions[swap_a], inverse_positions[swap_b] = log_b, log_a
                    out.append(TesseraInstruction(ins.name, [path[-2], path[-1]], ins.clbits, ins.params))
            elif len(ins.qubits) > 2:
                raise ValueError(f"Tessera: BasicSwapRouter encountered a {len(ins.qubits)}-qubit gate '{ins.name}'. Decompose to 2-qubit gates first using BasisTranslationPass.")

        return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, out, layout)