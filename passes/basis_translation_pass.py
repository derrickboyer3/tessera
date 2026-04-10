'''
    Basis Translation Pass
    ----------------------
    Transpiler pass that converts a TesseraCircuit into a backend-compatible circuit by replacing
    all non-basis gates with equivalent sequences of basis gates supported by the target backend.

    Each backend defines its own set of supported gates (basis gate set) and a decomposition map
    that specifies how to break down non-basis gates into basis gate sequences. This pass walks
    every instruction in the circuit and either passes it through unchanged (if it is already a
    basis gate or a measurement) or substitutes it with its decomposed equivalent, remapping
    qubit indices appropriately.

    Supported Backends:
        - IBM: {cx, rz, sx, x, u}

    Raises:
        ValueError: If a gate has no decomposition defined for the target backend.

    Defaults to IBM if no backend is specified.
'''
from circuit import TesseraCircuit
from instruction import TesseraInstruction
from transpiler_pass import TranspilerPass
from backends.backend_registry import BACKEND_REGISTRY

class BasisTranslationPass(TranspilerPass):
    def __init__(self, backend="IBM"):
        if backend not in BACKEND_REGISTRY:
            raise ValueError(f"Tessera: Unknown backend '{backend}'. Available backends: {list(BACKEND_REGISTRY.keys())}")
        self.backend = backend
        self.basis_gates = BACKEND_REGISTRY[backend]["basis_gates"]
        self.decomp_map = BACKEND_REGISTRY[backend]["decomp_map"]

    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        num_qubits = circuit.num_qubits
        num_clbits = circuit.num_clbits
        instructions = []
        for ins in circuit.instructions:
            if ins.name == "cnot":
                ins.name = "cx"
            if ins.name in ("measure", "barrier"):
                instructions.append(ins)
                continue
            if ins.name in self.basis_gates:
                instructions.append(ins)
            else:
                if ins.name not in self.decomp_map:
                    raise ValueError(f"Tessera: No decomposition found for gate '{ins.name}' in {self.backend} backend")
                decomp = self.decomp_map[ins.name]
                gates = decomp(ins.params) if callable(decomp) else decomp
                for gate in gates:
                    actual_qubits = [ins.qubits[i] for i in gate.qubits]
                    instructions.append(TesseraInstruction(gate.name, actual_qubits, ins.clbits, gate.params))
        return TesseraCircuit(num_qubits, num_clbits, instructions)