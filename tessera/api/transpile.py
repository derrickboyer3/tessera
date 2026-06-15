'''
    Tessera Top-Level Transpile Function
    -------------------------------------
    Public API entry point for the Tessera transpiler. Accepts a Qiskit circuit and
    transpiles it for the target backend by running the full Tessera pass pipeline:
    basis translation, layout, routing, and optimization.

    Args:
        circuit:      A Qiskit QuantumCircuit to transpile
        backend:      Backend name string matching an entry in BACKEND_REGISTRY (default: "IBM")
        coupling_map: One of three options:
                        - A TesseraCouplingMap instance to use directly
                        - A string key referencing an entry in COUPLING_MAP_REGISTRY
                        - None (default): uses the default coupling map for the chosen backend
        pathfinder:   Routing algorithm for the swap router. Either a registered name ("bfs", "a_star", "sabre")
                      or a custom pairwise callable (start, end) -> list[int]. Defaults to "bfs". None is treated as "bfs".
        strict:       If True, optimization passes use strict adjacency mode (default: True)
        epsilon:      Threshold for dropping near-zero rotation angles (default: 1e-9)
        optimization_iterations: 1 (default) | positive int = fixed iterations | -1 = run until gate count converges
        max_iterations:          Safety cap on loop iterations when optimization_iterations is -1 (default: 1000)
        layout_algorithm:        Layout algorithm for qubit placement. Either a registered name ("dense", "sabre", "trivial")
                                 or a custom callable (circuit, coupling_map) -> dict[int, int]. Defaults to "dense".
        debug_on:     If True, prints per-pass gate counts and total transpile time (default: False)

    Returns:
        A transpiled Qiskit QuantumCircuit compatible with the target backend

    Raises:
        ValueError: If the backend is not found in BACKEND_REGISTRY
        ValueError: If a string coupling_map key is not found in COUPLING_MAP_REGISTRY
        ValueError: If the circuit has more qubits than the resolved coupling map supports

    Example:
        from qiskit import QuantumCircuit
        from api.transpile import transpile

        qc = QuantumCircuit(3)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        transpiled = transpile(qc, backend="IBM")
'''
import time
from tessera.backends.backend_registry import BACKEND_REGISTRY
from tessera.backends.coupling_maps import COUPLING_MAP_REGISTRY
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.transpiler import TesseraTranspiler

def transpile(circuit, backend="IBM", coupling_map=None, pathfinder=None, strict=True, epsilon=1e-9, optimization_iterations=1, max_iterations=1000, layout_algorithm="dense", debug_on=False):
    # Step 1: Validate Backend
    if backend not in BACKEND_REGISTRY:
        raise ValueError(f"[Tessera]: Backend chosen does not exist in current BACKEND_REGISTRY.\n\tChosen {backend}\n\tTry \"IBM\"")

    resolved_coupling_map = None
    if isinstance(coupling_map, TesseraCouplingMap):
        resolved_coupling_map = coupling_map
    elif isinstance(coupling_map, str):
        if coupling_map not in COUPLING_MAP_REGISTRY:
            raise ValueError(f"Coupling map key '{coupling_map}' not found in COUPLING_MAP_REGISTRY.")
        resolved_coupling_map = COUPLING_MAP_REGISTRY[coupling_map]
    else:
        resolved_coupling_map = COUPLING_MAP_REGISTRY[BACKEND_REGISTRY[backend]["coupling_map"]]

    if circuit.num_qubits > resolved_coupling_map.num_qubits:
        raise ValueError(f"Circuit with {circuit.num_qubits} qubits is too big for coupling map with {resolved_coupling_map.num_qubits} qubits.")

    
    transpiler = TesseraTranspiler(circuit, resolved_coupling_map, backend, pathfinder, strict, epsilon, optimization_iterations, max_iterations, layout_algorithm, debug_on)
    start = time.perf_counter()
    result = transpiler.execute()
    elapsed = time.perf_counter() - start

    if debug_on:
        print(f"[Tessera] Circuit transpiled in {elapsed} seconds.")

    return result