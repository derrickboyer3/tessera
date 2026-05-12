'''
    Tessera Coupling Map Registry
    -----------------------------
    Provides pre-built TesseraCouplingMap instances derived from real IBM hardware
    topologies using Qiskit's fake provider backends. These are used as defaults
    when no custom coupling map is provided to the transpiler.

    Available maps:
        - IBM_DEFAULT:   FakeNairobi  —  7 qubits, heavy-hex topology (default)
        - IBM_BRISBANE:  FakeBrisbane — 127 qubits, heavy-hex topology
        - IBM_SHERBROOKE: FakeSherbrooke — 127 qubits, heavy-hex topology
        - IONQ_ARIA:    25 qubits, all-to-all connectivity (default)
        - IONQ_FORTE:   36 qubits, all-to-all connectivity
        - RIGETTI_ANKAA: 84 qubits, rectangular grid topology (default)
        - RIGETTI_ANKAA_9Q: 9 qubits, square lattice topology (Ankaa-9Q-3, default small device)

    The COUPLING_MAP_REGISTRY dict maps string keys to TesseraCouplingMap instances.
    These keys are referenced in the BACKEND_REGISTRY to associate each backend
    with its default hardware topology.
'''
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2, FakeBrisbane, FakeSherbrooke
from tessera.hardware.coupling_map import TesseraCouplingMap

# IBM Coupling Maps

def _build_ibm_default_coupling_map():
    backend = FakeNairobiV2()
    edges = list(backend.coupling_map.get_edges())
    return TesseraCouplingMap(backend.num_qubits, edges)

IBM_DEFAULT_COUPLING_MAP = _build_ibm_default_coupling_map()

def _build_ibm_brisbane_coupling_map():
    backend = FakeBrisbane()
    edges = list(backend.coupling_map.get_edges())
    return TesseraCouplingMap(backend.num_qubits, edges)

IBM_BRISBANE_COUPLING_MAP = _build_ibm_brisbane_coupling_map()

def _build_ibm_sherbrooke_coupling_map():
    backend = FakeSherbrooke()
    edges = list(backend.coupling_map.get_edges())
    return TesseraCouplingMap(backend.num_qubits, edges)

IBM_SHERBROOKE_COUPLING_MAP = _build_ibm_sherbrooke_coupling_map()

# IonQ Coupling Maps

# IonQ's topology is simple: all-to-all connectivity. We can represent this with a complete graph where every qubit is connected to every other qubit.
def _build_ionq_all_to_all(num_qubits):
    edges = [(i, j) for i in range(num_qubits) for j in range(num_qubits) if i != j]
    return TesseraCouplingMap(num_qubits, edges)

IONQ_ARIA_COUPLING_MAP = _build_ionq_all_to_all(25)  # IonQ Aria has 25 qubits
IONQ_FORTE_COUPLING_MAP = _build_ionq_all_to_all(36)  # IonQ Forte has 36 qubits

# Rigetti Coupling Maps

def _build_rigetti_rectangular_grid(rows, cols):
    num_qubits = rows * cols
    edges = []
    for r in range(rows):
        for c in range(cols):
            q = r * cols + c
            if c + 1 < cols:
                edges.extend([(q, q + 1), (q + 1, q)])
            if r + 1 < rows:
                edges.extend([(q, q + cols), (q + cols, q)])
    return TesseraCouplingMap(num_qubits, edges)

RIGETTI_ANKAA_COUPLING_MAP = _build_rigetti_rectangular_grid(7, 12)   # Ankaa-2, 84 qubits
RIGETTI_ANKAA_9Q_COUPLING_MAP = _build_rigetti_rectangular_grid(3, 3)  # Ankaa-9Q-3, 9 qubits

# Central registry mapping coupling map names to their corresponding TesseraCouplingMap instances

COUPLING_MAP_REGISTRY = {
    "IBM_DEFAULT": IBM_DEFAULT_COUPLING_MAP,
    "IBM_BRISBANE": IBM_BRISBANE_COUPLING_MAP,
    "IBM_SHERBROOKE": IBM_SHERBROOKE_COUPLING_MAP,
    "IONQ_ARIA": IONQ_ARIA_COUPLING_MAP,
    "IONQ_FORTE": IONQ_FORTE_COUPLING_MAP,
    "RIGETTI_ANKAA": RIGETTI_ANKAA_COUPLING_MAP,
    "RIGETTI_ANKAA_9Q": RIGETTI_ANKAA_9Q_COUPLING_MAP
}