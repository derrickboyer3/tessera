'''
    Tessera Transpiler
    ------------------
    The Tessera Transpiler is the class that allows a user to transpile their Qiskit circuit for a specific backend. It is initialized with
    the circuit itself, the backend the user wants to use (IBM, etc.), and it creates a TesseraPassManager to execute the transpilation on.
    The execute function takes the Qiskit circuit, converts it to a Tessera circuit, runs through each pass for the pass manager, converts 
    the transpiled Tessera circuit back to Qiskit, and returns. Optional debug logs can be enabled on initialization via the debug_on flag.

    High Level Overview:
                                                            (optional debug logs show here)
    +----------------+   from_qiskit()   +-----------------+   TesseraPassManager.run()   +----------------------------+
    | Qiskit Circuit |  ==============>  | Tessera Circuit |  =========================>  | Transpiled Tessera Circuit | 
    +----------------+                   +-----------------+                              +----------------------------+
                                                                                                        |
                                                                                                        | to_qiskit()
                                                                                                        V
                                        return back                                        +---------------------------+
    <====================================================================================  | Transpiled Qiskit Circuit |
                                                                                           +---------------------------+

    More passes and iterations to come
'''
from converters import from_qiskit, to_qiskit
from pass_manager import TesseraPassManager
from passes.basis_translation_pass import BasisTranslationPass

def log_before(pass_, circuit):
    print(f"[Tessera] Running pass: {pass_.name} | Gates: {len(circuit.instructions)}")

def log_after(pass_, circuit):
    print(f"[Tessera] Finished pass: {pass_.name} | Gates: {len(circuit.instructions)}")

class TesseraTranspiler:
    def __init__(self, circuit, backend="IBM", debug_on=False):
        self.circuit = circuit
        self.backend = backend
        passes = [BasisTranslationPass(self.backend)]
        self.pass_manager = TesseraPassManager(passes)
        self.debug_on = debug_on

    def execute(self):
        tes_circ = from_qiskit(self.circuit)
        trans_circ = self.pass_manager.run(tes_circ, before=log_before if self.debug_on else None, after=log_after if self.debug_on else None)
        qis_circ = to_qiskit(trans_circ)
        return qis_circ
        
