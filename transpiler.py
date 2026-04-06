from converters import from_qiskit, to_qiskit
from pass_manager import TesseraPassManager
from passes.basis_translation_pass import BasisTranslationPass

def log_before(pass_, circuit):
    print(f"[Tessera] Running pass: {pass_.name} | Gates: {len(circuit.instructions)}")

def log_after(pass_, circuit):
    print(f"[Tessera] Finished pass: {pass_.name} | Gates: {len(circuit.instructions)}")

class TesseraTranspiler:
    def __init__(self, circuit, backend="IBM"):
        self.circuit = circuit
        self.backend = backend
        passes = [BasisTranslationPass(self.backend)]
        self.pass_manager = TesseraPassManager(passes)

    def execute(self):
        tes_circ = from_qiskit(self.circuit)
        trans_circ = self.pass_manager.run(tes_circ, before=log_before, after=log_after)
        qis_circ = to_qiskit(trans_circ)
        return qis_circ
        
