'''
    Layout Pass
    -----------
    Transpiler pass that assigns logical qubits to physical qubits on the target
    hardware. Delegates the actual placement to a layout algorithm selected at
    construction time, then attaches the resulting mapping to the circuit so that
    subsequent passes (routing in particular) can translate logical qubit indices
    into physical ones.

    The layout algorithm is pluggable. Pass either a registered algorithm name
    (string) or a custom callable that matches the layout function signature:

        layout_fn(circuit: TesseraCircuit, coupling_map: TesseraCouplingMap) -> dict[int, int]

    String names are resolved through LAYOUT_REGISTRY at construction time, so
    unknown algorithm names fail immediately rather than at run time.

    Args:
        coupling_map:     The TesseraCouplingMap representing hardware connectivity
        layout_algorithm: A registered algorithm name (e.g. "dense") or a custom
                          callable matching the signature above. Defaults to "dense".

    Available algorithms:
        - "dense": greedy interaction-frequency placement (see tessera/layouts/dense.py)

    Raises:
        ValueError: If layout_algorithm is a string that is not registered in LAYOUT_REGISTRY.
        ValueError: If layout_algorithm is neither a string nor a callable.
'''
from tessera.circuit import TesseraCircuit
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.transpiler_pass import TranspilerPass
from tessera.layouts.layout_registry import LAYOUT_REGISTRY

class LayoutPass(TranspilerPass):
    def __init__(self, coupling_map: TesseraCouplingMap, layout_algorithm="dense"):
        self.coupling_map = coupling_map
        if isinstance(layout_algorithm, str):
            if layout_algorithm not in LAYOUT_REGISTRY:
                raise ValueError(f"[Tessera]: Unknown layout algorithm '{layout_algorithm}'. Available algorithms: {list(LAYOUT_REGISTRY.keys())}")
            self.layout_fn = LAYOUT_REGISTRY[layout_algorithm]
        elif callable(layout_algorithm):
            self.layout_fn = layout_algorithm
        else:
            raise ValueError(f"[Tessera]: layout_algorithm must be a string or callable, got {type(layout_algorithm)}")

    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        layout = self.layout_fn(circuit, self.coupling_map)
        return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, circuit.instructions, layout)