'''
    SABRE Routing Algorithm
    -----------------------
    Whole-circuit swap-selection routing based on Li, Ding, Xie (2019),
    "Tackling the Qubit Mapping Problem for NISQ-Era Quantum Devices."

    Unlike pairwise routers (BFS, A*) which find a path between two specific
    qubits each time a non-adjacent two-qubit gate appears, SABRE walks the
    circuit while maintaining a "front layer" of currently-executable gates
    and at each stuck point picks the single best swap by scoring candidates
    against a heuristic that considers both the front layer and an extended
    lookahead set.

    Algorithm:
        1. Build a front layer: instructions with no earlier dependency on
           any of their qubits.
        2. Greedily emit every front-layer gate that can execute under the
           current logical-to-physical mapping (single qubit, measurement,
           barrier, or two-qubit gate whose physical qubits are already
           adjacent on the coupling map).
        3. If gates remain but no front-layer gate can execute, generate
           candidate swaps: every edge of the coupling map adjacent to a
           qubit involved in any front-layer two-qubit gate.
        4. Score each candidate with the SABRE heuristic:

               H(swap) = (1/|F|) * Σ_{g in F} D(map'[g.q0], map'[g.q1])
                       + W * (1/|E|) * Σ_{g in E} D(map'[g.q0], map'[g.q1])

           where F is the front layer, E is the extended set (the next
           EXTENDED_SET_SIZE two-qubit gates after the front layer), map'
           is the mapping that would result from tentatively applying the
           swap, D is the coupling map hop distance, and W is the lookahead
           weight. Lower scores are better.
        5. Apply the best swap (emit a swap instruction and update the
           mapping), then return to step 1.

    Single qubit gates, measurements, and barriers are emitted with their
    qubit indices translated to the current physical mapping.

    Gates with more than 2 qubits raise a ValueError — run
    BasisTranslationPass first to decompose them into 2-qubit gates.

    Parameters:
        EXTENDED_SET_SIZE: Number of two-qubit gates beyond the front layer
                           that contribute to the lookahead term (default 20).
        LOOKAHEAD_WEIGHT:  Weight applied to the extended-set contribution
                           in the heuristic (default 0.5).

    Notes:
        This implementation omits the per-qubit decay term from the original
        paper. The decay term discourages repeatedly swapping the same qubit
        to spread swap activity across the device. It is a refinement, not
        a correctness requirement, and can be added later if benchmarks
        warrant it.

    Raises:
        ValueError: If no layout is found on the circuit.
        ValueError: If a gate with more than 2 qubits is encountered.
        ValueError: If routing gets stuck with no valid candidate swaps.
'''
from tessera.circuit import TesseraCircuit
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.instruction import TesseraInstruction

EXTENDED_SET_SIZE = 20
LOOKAHEAD_WEIGHT = 0.5


def compute_front_layer(remaining):
    # An instruction is in the front layer if no earlier remaining instruction
    # touches any of its qubits.
    front = []
    blocked_qubits = set()
    for ins in remaining:
        if any(q in blocked_qubits for q in ins.qubits):
            blocked_qubits.update(ins.qubits)
            continue
        front.append(ins)
        blocked_qubits.update(ins.qubits)
    return front


def is_executable(ins, mapping, coupling_map):
    if ins.name in ("measure", "barrier"):
        return True
    if len(ins.qubits) == 1:
        return True
    if len(ins.qubits) == 2:
        p0, p1 = mapping[ins.qubits[0]], mapping[ins.qubits[1]]
        return coupling_map.are_connected(p0, p1)
    raise ValueError(f"Tessera: SABRE routing encountered a {len(ins.qubits)}-qubit gate '{ins.name}'. Decompose to 2-qubit gates first using BasisTranslationPass.")


def translate(ins, mapping):
    physical = [mapping[q] for q in ins.qubits]
    return TesseraInstruction(ins.name, physical, ins.clbits, ins.params)


def candidate_swaps(front, mapping, coupling_map):
    # Every edge of the coupling map adjacent to a qubit involved in any
    # front-layer 2q gate. Includes edges to unmapped physical qubits so
    # SABRE can route through "spare" qubits on coupling maps larger than
    # the circuit. Deduplicated by sorting endpoints.
    involved = set()
    for ins in front:
        if len(ins.qubits) == 2:
            involved.add(mapping[ins.qubits[0]])
            involved.add(mapping[ins.qubits[1]])
    swaps = set()
    for p in involved:
        for n in coupling_map.neighbors(p):
            swaps.add(tuple(sorted((p, n))))
    return list(swaps)


def compute_extended_set(remaining, front, size):
    # The next `size` two-qubit gates after the front layer.
    front_ids = {id(g) for g in front}
    extended = []
    for ins in remaining:
        if id(ins) in front_ids:
            continue
        if len(ins.qubits) == 2:
            extended.append(ins)
            if len(extended) >= size:
                break
    return extended


def heuristic_score(swap, front, extended, mapping, coupling_map, lookahead_weight):
    # Build the mapping that would result from tentatively applying the swap.
    # Handles the case where one endpoint of the swap is a physical qubit
    # currently unoccupied by any logical qubit (sparse layout).
    p0, p1 = swap
    inverse = {v: k for k, v in mapping.items()}
    log0 = inverse.get(p0)
    log1 = inverse.get(p1)
    new_mapping = dict(mapping)
    if log0 is not None:
        new_mapping[log0] = p1
    if log1 is not None:
        new_mapping[log1] = p0

    def layer_cost(layer):
        total = 0
        count = 0
        for ins in layer:
            if len(ins.qubits) != 2:
                continue
            total += coupling_map.distance(new_mapping[ins.qubits[0]], new_mapping[ins.qubits[1]])
            count += 1
        return total / count if count else 0

    return layer_cost(front) + lookahead_weight * layer_cost(extended)


def sabre_route(circuit: TesseraCircuit, coupling_map: TesseraCouplingMap) -> TesseraCircuit:
    layout = circuit.layout
    if not layout:
        raise ValueError("Tessera: No layout found on circuit. Run a layout pass before SABRE routing.")

    mapping = dict(layout)
    inverse = {v: k for k, v in mapping.items()}
    remaining = list(circuit.instructions)
    output = []

    while remaining:
        front = compute_front_layer(remaining)

        # Step 1: drain everything in the front layer that can run under the current mapping.
        progress = True
        while progress and remaining:
            progress = False
            for ins in list(front):
                if is_executable(ins, mapping, coupling_map):
                    output.append(translate(ins, mapping))
                    remaining.remove(ins)
                    front = compute_front_layer(remaining)
                    progress = True
                    break

        if not remaining:
            break

        # Step 2: stuck — pick the best swap by scoring candidates against the heuristic.
        extended = compute_extended_set(remaining, front, EXTENDED_SET_SIZE)
        candidates = candidate_swaps(front, mapping, coupling_map)
        if not candidates:  # pragma: no cover
            raise ValueError("Tessera: SABRE routing found no valid candidate swaps but front layer has unexecutable gates. Coupling map may be malformed.")

        best = min(candidates, key=lambda sw: heuristic_score(sw, front, extended, mapping, coupling_map, LOOKAHEAD_WEIGHT))

        # Step 3: emit the swap and update the mapping. Handle the sparse-layout
        # case where one endpoint of the swap may not have a logical qubit on it.
        p0, p1 = best
        output.append(TesseraInstruction("swap", [p0, p1], [], []))
        log0 = inverse.get(p0)
        log1 = inverse.get(p1)
        if log0 is not None:
            mapping[log0] = p1
        if log1 is not None:
            mapping[log1] = p0
        if log0 is not None and log1 is not None:
            inverse[p0], inverse[p1] = log1, log0
        elif log0 is not None:
            inverse[p1] = log0
            del inverse[p0]
        elif log1 is not None:  # pragma: no cover
            # In SABRE, candidate swaps are sorted tuples (lower_index, higher_index),
            # and min() breaks ties lexicographically. When two equally-good swaps tie
            # — one (mapped, unmapped), one (unmapped, mapped) — the mapped one usually
            # has the lower index and wins. Kept for symmetry with the elif log0 branch.
            inverse[p0] = log1
            del inverse[p1]

    return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, output, layout)
