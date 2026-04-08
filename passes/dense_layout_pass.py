'''
    Dense Layout Pass
    -----------------
    A layout pass that intelligently maps logical qubits to physical qubits by
    analyzing interaction frequency in the circuit. Qubits that interact more
    frequently are placed on physical qubits that are closer together on the
    coupling map, minimizing the number of swap gates needed during routing.

    Algorithm:
        1. Build an interaction map counting how often each qubit pair interacts
        2. Sort pairs by interaction frequency (highest first)
        3. Greedily assign physical qubits — frequently interacting pairs get
           placed on physically close qubits first
        4. Assign any remaining unplaced logical qubits to leftover physical qubits

    Raises:
        ValueError: If the circuit has more qubits than the coupling map supports.
'''
from circuit import TesseraCircuit
from hardware.coupling_map import TesseraCouplingMap
from transpiler_pass import TranspilerPass
from itertools import combinations
from collections import defaultdict

class DenseLayoutPass(TranspilerPass):
    def __init__(self, coupling_map: TesseraCouplingMap):
        self.coupling_map = coupling_map

    def find_closest_free(self, physical_qubit, taken):
        best = None
        best_dist = float('inf')
        for p in range(self.coupling_map.num_qubits):
            if p not in taken:
                try:
                    d = self.coupling_map.distance(physical_qubit, p)
                    if d < best_dist:
                        best_dist = d
                        best = p
                except ValueError:
                    continue
        return best

    def find_closest_pair(self, taken):
        best_p0, best_p1 = None, None
        best_dist = float('inf')
        available = [p for p in range(self.coupling_map.num_qubits) if p not in taken]
        for p0, p1 in combinations(available, 2):
            try:
                d = self.coupling_map.distance(p0, p1)
                if d < best_dist:
                    best_dist = d
                    best_p0, best_p1 = p0, p1
            except ValueError:
                continue
        return best_p0, best_p1

    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        # Step 0: Validation & Set Up
        if circuit.num_qubits > len(self.coupling_map):
            raise ValueError(f"[Tessera]: Circuit has too many qubits for coupling map:\n\tCircuit Qubits: {circuit.num_qubits}\n\tCoupling Map Length: {len(self.coupling_map)}")
        num_qubits = circuit.num_qubits
        num_clbits = circuit.num_clbits
        instructions = circuit.instructions

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
        assigned = set()    # logical qubits already placed
        taken = set()       # physical qubits already used
        for (q0, q1), count in sorted_interactions:
            if q0 not in assigned and q1 not in assigned:
                # Neither placed yet — find the two closest physical qubits
                best_p0, best_p1 = self.find_closest_pair(taken)
                layout[q0] = best_p0
                layout[q1] = best_p1
                assigned.add(q0)
                assigned.add(q1)
                taken.add(best_p0)
                taken.add(best_p1)
            elif q0 in assigned and q1 not in assigned:
                # q0 placed, find closest free physical qubit to layout[q0]
                best_p1 = self.find_closest_free(layout[q0], taken)
                layout[q1] = best_p1
                assigned.add(q1)
                taken.add(best_p1)
            elif q1 in assigned and q0 not in assigned:
                # q1 placed, find closest free physical qubit to layout[q1]
                best_p0 = self.find_closest_free(layout[q1], taken)
                layout[q0] = best_p0
                assigned.add(q0)
                taken.add(best_p0)
        
        # Step 4: Assign remaining unplaced logical qubits
        remaining_physical = [p for p in range(self.coupling_map.num_qubits) if p not in taken]
        for q in range(num_qubits):
            if q not in assigned:
                layout[q] = remaining_physical.pop(0)

        return TesseraCircuit(num_qubits, num_clbits, instructions, layout)

