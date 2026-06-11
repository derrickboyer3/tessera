'''
    Pairwise Routing Engine
    -----------------------
    Shared SWAP-insertion engine for all pairwise (path-finder based) routing
    strategies. Walks the circuit instruction by instruction; for each
    instruction it translates the logical qubit indices into physical qubits
    using the current logical-to-physical mapping (which starts equal to
    circuit.layout and is updated whenever a SWAP is inserted). For two-qubit
    gates whose translated physical qubits are not adjacent on the coupling
    map, calls the supplied path_finder to obtain a path of physical qubits
    and inserts SWAP gates along it to bring the operands adjacent before
    the gate runs.

    Single qubit gates, measurements, and barriers are emitted with their
    qubit indices translated to the current physical mapping.

    Gates with more than 2 qubits raise a ValueError — run
    BasisTranslationPass first to decompose them into 2-qubit gates.

    This function is the foundation under the BFS and A* routing strategies
    in ROUTING_REGISTRY. SABRE routing does not use this engine because its
    algorithm operates over the whole circuit rather than along pairwise
    paths.

    Args:
        circuit:      The TesseraCircuit to route. Must have a populated layout.
        coupling_map: The TesseraCouplingMap representing hardware connectivity.
        path_finder:  Callable (start, end) -> list[int] returning a path of
                      physical qubits from start to end (inclusive on both ends).

    Returns:
        A new TesseraCircuit with SWAPs inserted and all qubit indices
        translated to physical qubits. circuit.layout is preserved as the
        initial mapping reference.

    Raises:
        ValueError: If the input circuit has no layout.
        ValueError: If a gate with more than 2 qubits is encountered.
'''
from tessera.circuit import TesseraCircuit
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.instruction import TesseraInstruction

def pairwise_route(circuit: TesseraCircuit, coupling_map: TesseraCouplingMap, path_finder) -> TesseraCircuit:
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
            if coupling_map.are_connected(p0, p1):
                out.append(TesseraInstruction(ins.name, [p0, p1], ins.clbits, ins.params))
            else:
                path = path_finder(p0, p1)
                for i in range(len(path) - 2):
                    swap_a = path[i]
                    swap_b = path[i + 1]
                    out.append(TesseraInstruction("swap", [swap_a, swap_b], [], []))
                    # Handle paths that go through physical qubits not currently
                    # mapped to any logical qubit (sparse layout). If a side has
                    # no logical qubit, the swap just moves the other side's
                    # logical qubit to the unmapped slot.
                    log_a = inverse_positions.get(swap_a)
                    log_b = inverse_positions.get(swap_b)
                    if log_a is not None:
                        current_positions[log_a] = swap_b
                    if log_b is not None:
                        current_positions[log_b] = swap_a
                    if log_a is not None and log_b is not None:
                        inverse_positions[swap_a], inverse_positions[swap_b] = log_b, log_a
                    elif log_a is not None:
                        inverse_positions[swap_b] = log_a
                        del inverse_positions[swap_a]
                    elif log_b is not None:  # pragma: no cover
                        # Unreachable in pairwise traversal: swap_a is always the
                        # node carrying the migrating logical qubit (source on
                        # the first swap, previous swap's destination after that),
                        # so log_a is always set. Kept for symmetry with sabre.
                        inverse_positions[swap_a] = log_b
                        del inverse_positions[swap_b]
                out.append(TesseraInstruction(ins.name, [path[-2], path[-1]], ins.clbits, ins.params))
        elif len(ins.qubits) > 2:
            raise ValueError(f"Tessera: BasicSwapRouter encountered a {len(ins.qubits)}-qubit gate '{ins.name}'. Decompose to 2-qubit gates first using BasisTranslationPass.")

    return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, out, layout)