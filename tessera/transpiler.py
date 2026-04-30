'''
    Tessera Transpiler
    ------------------
    The Tessera Transpiler is the class that allows a user to transpile their Qiskit circuit for a specific backend. It is initialized with
    the circuit itself, a CouplingMap representing the target hardware topology, the backend the user wants to use (IBM, etc.), an optional
    custom path-finding strategy, an optional strict flag for optimization passes, an optional epsilon for rotation merging, and an optional
    debug flag. The execute function takes the Qiskit circuit, converts it to a Tessera circuit, runs through each pass in the pass manager,
    converts the transpiled Tessera circuit back to Qiskit, and returns.

    High Level Overview:

                     (Conversion Stage 1)
                                                                    (optional debug logs show here)
    +----------------+   from_qiskit()   +-----------------+          TesseraPassManager.run()
    | Qiskit Circuit |  ==============>  | Tessera Circuit |  ================================================
    +----------------+                   +-----------------+                                                 |
                                                                                                             |
                                          Pass 1                    Pass 2                    Pass 3         |
                                   +--------------------+   +--------------------+   +--------------------+  |
                                   | BasisTranslation   |-->|   DenseLayout      |-->|  BasicSwapRouter   |<-+
             (Transpilation Stage) | Decompose gates to |   | Map logical qubits |   | Apply layout and   |
                                   | backend basis set  |   | to physical qubits |   | insert SWAP gates  |
                                   +--------------------+   +--------------------+   +--------------------+
                                                                                                |
                                                                                                V
                                          Pass 4                    Pass 5                    Pass 6
                                   +--------------------+   +--------------------+   +--------------------+
                                   | RemoveBarriers     |-->| CancelAdjacent     |-->| MergeRotations     |
              (Optimization Stage) | Strip barrier      |   | Remove self-inverse|   | Combine consecutive|
                                   | instructions       |   | gate pairs         |   | rotation gates     |
                                   +--------------------+   +--------------------+   +--------------------+
                                                                                                |
                                                                                                | to_qiskit()
                                                                                                V
                                        return back                              +---------------------------+
    <============================================================================| Transpiled Qiskit Circuit |
                                                                                 +---------------------------+
                                            (Conversion Stage 2)
'''
from tessera.converters import from_qiskit, to_qiskit
from tessera.pass_manager import TesseraPassManager
from tessera.passes.basis_translation_pass import BasisTranslationPass
from tessera.passes.dense_layout_pass import DenseLayoutPass
from tessera.passes.basic_swap_router import BasicSwapRouter
from tessera.passes.remove_barriers_pass import RemoveBarriersPass
from tessera.passes.cancel_adjacent_pass import CancelAdjacentPass
from tessera.passes.merge_rotations_pass import MergeRotationsPass

def log_before(pass_, circuit):
    print(f"[Tessera] Running pass: {pass_.name} | Gates: {len(circuit.instructions)}")

def log_after(pass_, circuit):
    print(f"[Tessera] Finished pass: {pass_.name} | Gates: {len(circuit.instructions)}")

class TesseraTranspiler:
    def __init__(self, circuit, coupling_map, backend="IBM", pathfinder=None, strict=True, epsilon=1e-9, debug_on=False):
        self.circuit = circuit
        self.backend = backend
        self.coupling_map = coupling_map
        self.path_finder = pathfinder
        self.strict = strict
        self.epsilon = epsilon
        passes = [
            BasisTranslationPass(self.backend), 
            DenseLayoutPass(self.coupling_map), 
            BasicSwapRouter(self.coupling_map, self.path_finder),
            RemoveBarriersPass(),
            CancelAdjacentPass(self.strict),
            MergeRotationsPass(self.strict, self.epsilon)
        ]
        self.pass_manager = TesseraPassManager(passes)
        self.debug_on = debug_on

    def execute(self):
        tes_circ = from_qiskit(self.circuit)
        trans_circ = self.pass_manager.run(tes_circ, before=log_before if self.debug_on else None, after=log_after if self.debug_on else None)
        qis_circ = to_qiskit(trans_circ)
        return qis_circ
        
