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

    The COUPLING_MAP_REGISTRY dict maps string keys to TesseraCouplingMap instances.
    These keys are referenced in the BACKEND_REGISTRY to associate each backend
    with its default hardware topology.
'''
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2, FakeBrisbane, FakeSherbrooke
from hardware.coupling_map import TesseraCouplingMap

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

COUPLING_MAP_REGISTRY = {
    "IBM_DEFAULT": IBM_DEFAULT_COUPLING_MAP,
    "IBM_BRISBANE": IBM_BRISBANE_COUPLING_MAP,
    "IBM_SHERBROOKE": IBM_SHERBROOKE_COUPLING_MAP
}