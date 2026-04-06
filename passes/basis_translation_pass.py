'''
    Basis Translation Pass
    ----------------------
    A first step pass to take a circuit and translate each gate into it's basis state (backend specific; default = IBM).
    This pass takes in a TesseraCircuit and goes through each instruction to convert it, so that the new circuit is formatted
    appropriately depending on where it is to be run.
'''
from circuit import TesseraCircuit
from instruction import TesseraInstruction
from transpiler_pass import TranspilerPass
from backends.decomposition_maps import IBM_DECOMP_MAP
from backends.basis_gate_sets import IBM_BASIS_GATES

class BasisTranslationPass(TranspilerPass):
    def __init__(self, backend="IBM"):
        self.backend = backend

    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        if self.backend == "IBM":
            num_qubits = circuit.num_qubits
            num_clbits = circuit.num_clbits
            instructions = []
            for ins in circuit.instructions:
                if ins.name == "cnot":
                    ins.name = "cx"
                if ins.name in IBM_BASIS_GATES:
                    instructions.append(ins)
                else:
                    if ins.name == "measure":
                        instructions.append(ins)
                        continue
                    if ins.name not in IBM_DECOMP_MAP:
                        raise ValueError(f"Tessera: No decomposition found for gate '{ins.name}' in {self.backend} backend")
                    decomp = IBM_DECOMP_MAP[ins.name]
                    gates = decomp(ins.params) if callable(decomp) else decomp
                    for gate in gates:
                        actual_qubits = [ins.qubits[i] for i in gate.qubits]
                        instructions.append(TesseraInstruction(gate.name, actual_qubits, ins.clbits, gate.params))
            return TesseraCircuit(num_qubits, num_clbits, instructions)
        else:    
            print("Unknown backend requested. Returning original circuit. Try using backend=\"IBM\"")
            return circuit