'''
    Tessera Transpiler
    ------------------
    The Tessera Transpiler is the class that allows a user to transpile their Qiskit circuit for a specific backend. It is initialized with
    the circuit itself, a CouplingMap representing the target hardware topology, the backend the user wants to use (IBM, etc.), an optional
    custom path-finding strategy, and an optional debug flag. The execute function takes the Qiskit circuit, converts it to a Tessera circuit,
    runs through each pass in the pass manager, converts the transpiled Tessera circuit back to Qiskit, and returns.

    High Level Overview:
                                                                        (optional debug logs show here)
    +----------------+   from_qiskit()   +-----------------+          TesseraPassManager.run()
    | Qiskit Circuit |  ==============>  | Tessera Circuit |  ================================================
    +----------------+                   +-----------------+                                                 |
                                                                                                             |
                                          Pass 1                    Pass 2                    Pass 3         |
                                   +--------------------+   +--------------------+   +--------------------+  |
                                   | BasisTranslation   |-->|   DenseLayout      |-->|  BasicSwapRouter   |<-+
                                   | Decompose gates to |   | Map logical qubits |   | Apply layout and   |
                                   | backend basis set  |   | to physical qubits |   | insert SWAP gates  |
                                   +--------------------+   +--------------------+   +--------------------+
                                                                                                |
                                                                                                | to_qiskit()
                                                                                                V
                                        return back                              +---------------------------+
    <============================================================================| Transpiled Qiskit Circuit |
                                                                                 +---------------------------+

    More passes and iterations to come
'''
from converters import from_qiskit, to_qiskit
from pass_manager import TesseraPassManager
from passes.basis_translation_pass import BasisTranslationPass
from passes.dense_layout_pass import DenseLayoutPass
from passes.basic_swap_router import BasicSwapRouter

def log_before(pass_, circuit):
    print(f"[Tessera] Running pass: {pass_.name} | Gates: {len(circuit.instructions)}")

def log_after(pass_, circuit):
    print(f"[Tessera] Finished pass: {pass_.name} | Gates: {len(circuit.instructions)}")

class TesseraTranspiler:
    def __init__(self, circuit, coupling_map, backend="IBM", pathfinder=None, debug_on=False):
        self.circuit = circuit
        self.backend = backend
        self.coupling_map = coupling_map
        self.path_finder = pathfinder
        passes = [BasisTranslationPass(self.backend), DenseLayoutPass(self.coupling_map), BasicSwapRouter(self.coupling_map, self.path_finder)]
        self.pass_manager = TesseraPassManager(passes)
        self.debug_on = debug_on

    def execute(self):
        tes_circ = from_qiskit(self.circuit)
        trans_circ = self.pass_manager.run(tes_circ, before=log_before if self.debug_on else None, after=log_after if self.debug_on else None)
        qis_circ = to_qiskit(trans_circ)
        return qis_circ
        
