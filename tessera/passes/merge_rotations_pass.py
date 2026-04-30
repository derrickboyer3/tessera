'''
    Merge Rotations Pass
    --------------------
    Transpiler pass that merges consecutive rotation gates on the same qubit into a single
    rotation. Since rotation gates are additive (Rz(θ1)·Rz(θ2) = Rz(θ1+θ2)), consecutive
    rotations of the same type on the same qubit can be collapsed into one. If the merged
    angle is approximately zero (within epsilon), the gate is dropped entirely.

    Operates in two modes:

    Strict mode (default): only merges gates that are directly adjacent in the instruction list.
    Note that three consecutive rotation gates will leave one unmerged in a single pass.
    Commutative mode: merges gates separated by instructions on non-overlapping qubits,
    since those instructions commute freely past each other.

    Supported mergeable gates: rz, rx, ry

    Examples:
        Strict:      Rz(0.3, q0) Rz(0.5, q0)              -> Rz(0.8, q0)
        Strict:      Rz(0.5, q0) Rz(-0.5, q0)             -> (dropped)
        Commutative: Rz(0.3, q0) Rx(0.5, q1) Rz(0.5, q0) -> Rz(0.8, q0) Rx(0.5, q1)

    This pass should be run after routing and basis translation.
'''
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.transpiler_pass import TranspilerPass

MERGEABLE_ROTATION_GATES = {"rz", "rx", "ry"}

class MergeRotationsPass(TranspilerPass):
    def __init__(self, strict=True, epsilon=1e-9):
        self.strict = strict
        self.epsilon = epsilon

    # Helper function for merging rotation gates that are directly next to each other in the instruction list
    # EX: rz(q0, pi / 4), rz(q0, pi / 4) -> rz(q0, pi / 2) because the rz gates can be combined into one
    def strict_inverse_dedup(self, circuit: TesseraCircuit) -> TesseraCircuit:
        result = []
        skip = set()
        ins = circuit.instructions

        for i in range(len(ins)):
            if i in skip:
                continue
            if ins[i].name not in MERGEABLE_ROTATION_GATES:
                result.append(ins[i])
                continue

            if i + 1 < len(ins) and ins[i].name == ins[i + 1].name and ins[i].qubits == ins[i + 1].qubits:
                merged_angle = ins[i].params[0] + ins[i + 1].params[0]
                skip.add(i + 1)
                if abs(merged_angle) < self.epsilon:
                    continue
                else:
                    result.append(TesseraInstruction(ins[i].name, ins[i].qubits, ins[i].clbits, [merged_angle]))
            else:
                result.append(ins[i])

        return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, result, circuit.layout)
        

    # Helper function for merging rotation gates that are not directly next to each other in the instruction list
    # EX: rz(q0, pi / 4), ry(q1, pi / 2), rz(q0, pi / 4) -> rz(q0, pi / 2), ry(q1, pi / 2) because the rz(q0) gates can be combined into one
    def commutative_inverse_dedup(self, circuit: TesseraCircuit) -> TesseraCircuit:
        result = []
        skip = set()
        ins = circuit.instructions

        for i in range(len(ins)):
            if i in skip:
                continue
            if ins[i].name not in MERGEABLE_ROTATION_GATES:
                result.append(ins[i])
                continue

            qubits_i = set(ins[i].qubits)
            merged = False
            for j in range(i + 1, len(ins)):
                qubits_j = set(ins[j].qubits)
                if qubits_i & qubits_j:
                    if ins[i].name == ins[j].name and ins[i].qubits == ins[j].qubits:
                        merged_angle = ins[i].params[0] + ins[j].params[0]
                        skip.add(j)
                        merged = True
                        if abs(merged_angle) >= self.epsilon:
                            result.append(TesseraInstruction(ins[i].name, ins[i].qubits, ins[i].clbits, [merged_angle]))
                    break

            if not merged:
                result.append(ins[i])

        return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, result, circuit.layout)
        

    # Transpiler pass run function
    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        if (self.strict):
            return self.strict_inverse_dedup(circuit)
        else:
            return self.commutative_inverse_dedup(circuit)
