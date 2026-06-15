'''
    Tessera Transpiler
    ------------------
    The Tessera Transpiler is the class that allows a user to transpile their Qiskit circuit for a specific backend. It is initialized with
    the circuit itself, a CouplingMap representing the target hardware topology, the backend the user wants to use (IBM, etc.), an optional
    pathfinder (routing algorithm name or pairwise callable, default "bfs"), an optional strict flag for optimization passes, an optional
    epsilon for rotation merging, an optional optimization_iterations count (1 default, positive int for fixed loops, -1 for convergence),
    an optional max_iterations safety cap for convergence mode, an optional layout_algorithm (string name or callable, default "dense"),
    and an optional debug flag. The execute function takes the Qiskit circuit, converts it to a Tessera circuit, runs through each pass
    in the pass manager, converts the transpiled Tessera circuit back to Qiskit, and returns.

    LayoutPass resolves layout_algorithm through LAYOUT_REGISTRY ("trivial", "dense", "sabre", or a custom callable).
    BasicSwapRouter resolves pathfinder through ROUTING_REGISTRY ("bfs", "a_star", "sabre", or a custom pairwise callable).

    High Level Overview:

                     (Conversion Stage 1)
                                                                    (optional debug logs show here)
    +----------------+   from_qiskit()   +-----------------+          TesseraPassManager.run()
    | Qiskit Circuit |  ==============>  | Tessera Circuit |  ================================================
    +----------------+                   +-----------------+                                                 |
                                                                                                             |
                                          Pass 1                    Pass 2                    Pass 3         |
                                   +--------------------+   +--------------------+   +--------------------+  |
                                   | BasisTranslation   |-->|       Layout       |-->|  BasicSwapRouter   |<-+
             (Transpilation Stage) | Decompose gates to |   | Map logical qubits |   | Apply layout and   |
                                   | backend basis set  |   | to physical qubits |   | insert SWAP gates  |
                                   +--------------------+   +--------------------+   +--------------------+
                                                                                                |
                                                                                                V
                                                                                             Pass 4
                                                                                +------------------------------+
                                                                                | BasisTranslation 2           |
                                                                                | Decompose any new SWAP gates |
                                                                                | and re-translate to basis    |
                                                                                +------------------------------+
                                                                                                |
                                                                                                V
                                                            Pass 5                            Pass 6
                                                    +--------------------+   +---------------------------------------+
                                                    | RemoveBarriers     |-->| OptimizationLoopPass                  |
                                    (Optimization)  | Strip barrier      |   | Loop the inner passes either N times  |
                                                    | instructions       |   | or until gate count converges:        |
                                                    +--------------------+   |  +---------------------+              |
                                                                             |  | CancelAdjacentPass  |              |
                                                                             |  +---------------------+              |
                                                                             |            |                          |
                                                                             |            V                          |
                                                                             |  +---------------------+              |
                                                                             |  | MergeRotationsPass  |              |
                                                                             |  +---------------------+              |
                                                                             +---------------------------------------+
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
from tessera.passes.layout_pass import LayoutPass
from tessera.passes.basic_swap_router import BasicSwapRouter
from tessera.passes.remove_barriers_pass import RemoveBarriersPass
from tessera.passes.cancel_adjacent_pass import CancelAdjacentPass
from tessera.passes.merge_rotations_pass import MergeRotationsPass
from tessera.passes.optimization_loop_pass import OptimizationLoopPass

def log_before(pass_, circuit):
    print(f"[Tessera] Running pass: {pass_.name} | Gates: {len(circuit.instructions)}")

def log_after(pass_, circuit):
    print(f"[Tessera] Finished pass: {pass_.name} | Gates: {len(circuit.instructions)}")

class TesseraTranspiler:
    def __init__(self, circuit, coupling_map, backend="IBM", pathfinder=None, strict=True, epsilon=1e-9, optimization_iterations=1, max_iterations=1000, layout_algorithm="dense", debug_on=False):
        self.circuit = circuit
        self.backend = backend
        self.coupling_map = coupling_map
        self.path_finder = pathfinder
        self.strict = strict
        self.epsilon = epsilon
        self.optimization_iterations = optimization_iterations
        self.max_iterations = max_iterations
        self.layout_algorithm = layout_algorithm
        self.debug_on = debug_on
        optimization_passes = [CancelAdjacentPass(self.strict), MergeRotationsPass(self.strict, self.epsilon)]
        passes = [
            BasisTranslationPass(self.backend), 
            LayoutPass(self.coupling_map, self.layout_algorithm), 
            BasicSwapRouter(self.coupling_map, self.path_finder),
            BasisTranslationPass(self.backend),  # Run basis translation again after routing to catch any new non-basis gates
            RemoveBarriersPass(),
            OptimizationLoopPass(optimization_passes, self.optimization_iterations, self.max_iterations, self.debug_on)
        ]
        self.pass_manager = TesseraPassManager(passes)

    def execute(self):
        tes_circ = from_qiskit(self.circuit)
        trans_circ = self.pass_manager.run(tes_circ, before=log_before if self.debug_on else None, after=log_after if self.debug_on else None)
        qis_circ = to_qiskit(trans_circ)
        return qis_circ
        
