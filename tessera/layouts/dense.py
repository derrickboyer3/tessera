'''
    Dense Layout Algorithm
    ----------------------
    Greedy interaction-frequency placement of logical qubits onto physical qubits.
    Qubits that interact more frequently in the circuit are placed on physical
    qubits that are closer together on the coupling map, minimizing the number
    of SWAP gates needed during routing.

    Algorithm:
        1. Count how often each logical qubit pair interacts in the circuit
        2. Sort pairs by interaction frequency (highest first)
        3. Greedily assign physical qubits — frequently interacting pairs get
           placed on physically close qubits first:
             - Neither qubit placed yet: pick the two closest free physical qubits
             - One already placed: pick the closest free physical qubit to it
        4. Assign any remaining unplaced logical qubits to leftover physical qubits

    Args:
        circuit:      The TesseraCircuit whose qubits need to be laid out
        coupling_map: The TesseraCouplingMap representing hardware connectivity

    Returns:
        dict[int, int] mapping logical qubit indices to physical qubit indices.

    Raises:
        ValueError: If the circuit has more qubits than the coupling map supports.
'''
from tessera.circuit import TesseraCircuit
from tessera.hardware.coupling_map import TesseraCouplingMap
from itertools import combinations
from collections import defaultdict

def find_closest_free(physical_qubit, taken, coupling_map):
    best = None
    best_dist = float('inf')
    for p in range(coupling_map.num_qubits):
        if p not in taken:
            try:
                d = coupling_map.distance(physical_qubit, p)
                if d < best_dist:
                    best_dist = d
                    best = p
            except ValueError:
                continue
    return best

def find_closest_pair(taken, coupling_map):
    best_p0, best_p1 = None, None
    best_dist = float('inf')
    available = [p for p in range(coupling_map.num_qubits) if p not in taken]
    for p0, p1 in combinations(available, 2):
        try:
            d = coupling_map.distance(p0, p1)
            if d < best_dist:
                best_dist = d
                best_p0, best_p1 = p0, p1
        except ValueError:
            continue
    return best_p0, best_p1

def dense_layout(circuit: TesseraCircuit, coupling_map: TesseraCouplingMap) -> dict[int, int]:
    # Step 0: Validation & Set Up
    if circuit.num_qubits > len(coupling_map):
        raise ValueError(f"[Tessera]: Circuit has too many qubits for coupling map:\n\tCircuit Qubits: {circuit.num_qubits}\n\tCoupling Map Length: {len(coupling_map)}")
    num_qubits = circuit.num_qubits

    # Step 1: Compute interaction counts
    interaction_counts = defaultdict(int)
    for ins in circuit.instructions:
        if len(ins.qubits) > 1:
            for q0, q1 in combinations(ins.qubits, 2):
                pair = tuple(sorted([q0, q1]))
                interaction_counts[pair] += 1

    # Step 2: Sort by highest interaction count
    sorted_interactions = sorted(interaction_counts.items(), key=lambda x: x[1], reverse=True)

    # Step 3: Assign physical qubits
    layout = {}
    assigned = set()
    taken = set()
    for (q0, q1), count in sorted_interactions:
        if q0 not in assigned and q1 not in assigned:
            best_p0, best_p1 = find_closest_pair(taken, coupling_map)
            layout[q0] = best_p0
            layout[q1] = best_p1
            assigned.add(q0); assigned.add(q1)
            taken.add(best_p0); taken.add(best_p1)
        elif q0 in assigned and q1 not in assigned:
            best_p1 = find_closest_free(layout[q0], taken, coupling_map)
            layout[q1] = best_p1
            assigned.add(q1)
            taken.add(best_p1)
        elif q1 in assigned and q0 not in assigned:
            best_p0 = find_closest_free(layout[q1], taken, coupling_map)
            layout[q0] = best_p0
            assigned.add(q0)
            taken.add(best_p0)

    # Step 4: Assign remaining unplaced logical qubits
    remaining_physical = [p for p in range(coupling_map.num_qubits) if p not in taken]
    for q in range(num_qubits):
        if q not in assigned:
            layout[q] = remaining_physical.pop(0)

    return layout