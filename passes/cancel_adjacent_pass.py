'''
    Cancel Adjacent Pass
    --------------------
    Transpiler pass that removes pairs of adjacent self-inverse gates that cancel each other out.
    A gate G is self-inverse if G·G = I, meaning applying it twice returns to the original state.
    This pass operates in two modes:

    Strict mode (default): only cancels gates that are directly adjacent in the instruction list.
    Commutative mode: cancels gates that are separated by instructions on non-overlapping qubits,
    since those instructions commute freely past each other.

    Supported self-inverse gates: x, cx, y, h, cz, swap

    Examples:
        Strict:      X(q0) X(q0)           -> (empty)
        Strict:      H(q0) X(q1) H(q0)     -> H(q0) X(q1) H(q0)  (no cancellation)
        Commutative: H(q0) X(q1) H(q0)     -> X(q1)              (H gates cancel)

    This pass should be run after routing and basis translation, as earlier passes may
    introduce new cancellable gate pairs during decomposition and SWAP insertion.
'''
from circuit import TesseraCircuit
from transpiler_pass import TranspilerPass

SELF_INVERSE_GATES = {"x", "cx", "y", "h", "cz", "swap"}

class CancelAdjacentPass(TranspilerPass):
    def __init__(self, strict=True):
        self.strict = strict

    # Helper function for removing gates that inverse each other and are directly next to each other in the instruction list
    # EX: x(q0), x(q0) -> remove the x(q0) the x gates inverse each other and they are unnecessary
    def strict_inverse_dedup(self, circuit: TesseraCircuit) -> TesseraCircuit:
        cancelled = set()

        ins = circuit.instructions
        for i in range(len(ins)):
            if i in cancelled or ins[i].name not in SELF_INVERSE_GATES:
                continue
            else:
                if i + 1 < len(ins) and ins[i].name == ins[i + 1].name and ins[i].qubits == ins[i + 1].qubits and i + 1 not in cancelled:
                    cancelled.add(i)
                    cancelled.add(i + 1)
                else:
                    continue

        dedupped_ins = []
        for i in range(len(ins)):
            if i in cancelled:
                continue
            else:
                dedupped_ins.append(ins[i])

        return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, dedupped_ins, circuit.layout)

    # Helper function for removing gates that inverse each other but are not directly next to each other in the instruction list
    # EX: x(q0), x(q1), x(q0) -> remove the x(q0) because nothing happens to q0 between them and they inverse each other
    def commutative_inverse_dedup(self, circuit: TesseraCircuit) -> TesseraCircuit:
        cancelled = set()

        ins = circuit.instructions
        for i in range(len(ins)):
            if i in cancelled or ins[i].name not in SELF_INVERSE_GATES:
                continue
            qubits_i = set(ins[i].qubits)
            for j in range(i + 1, len(ins)):
                if j in cancelled:
                    continue
                qubits_j = set(ins[j].qubits)
                if qubits_i & qubits_j:
                    if ins[i].name == ins[j].name and ins[i].qubits == ins[j].qubits:
                        cancelled.add(i)
                        cancelled.add(j)
                    break
                
        dedupped_ins = [ins[i] for i in range(len(ins)) if i not in cancelled]
        return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, dedupped_ins, circuit.layout)

    # Transpiler pass run function
    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        if (self.strict):
            return self.strict_inverse_dedup(circuit)
        else:
            return self.commutative_inverse_dedup(circuit)
