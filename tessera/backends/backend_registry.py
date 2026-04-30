'''
    Tessera Backend Registry
    ------------------------
    Central registry mapping backend names to their corresponding basis gate sets,
    decomposition maps, and default coupling maps. When adding a new backend, import
    its basis gate set and decomposition map, add a coupling map entry to the
    COUPLING_MAP_REGISTRY in coupling_maps.py, and add a new entry here. No other
    files need to change.

    Each entry contains:
        - basis_gates:  set of gate name strings supported by the backend
        - decomp_map:   dict mapping non-basis gate names to decomposition sequences
        - coupling_map: string key referencing an entry in COUPLING_MAP_REGISTRY,
                        representing the default hardware topology for this backend

    Available backends:
        - IBM: basis gates {cx, rz, sx, x, u}, defaults to FakeNairobi (7 qubit) topology
'''
from tessera.backends.basis_gate_sets import IBM_BASIS_GATES
from tessera.backends.decomposition_maps import IBM_DECOMP_MAP

BACKEND_REGISTRY = {
    "IBM": {
        "basis_gates": IBM_BASIS_GATES,
        "decomp_map": IBM_DECOMP_MAP,
        "coupling_map": "IBM_DEFAULT"
    }
    # Add new backend registrations here
}
from tessera.backends.basis_gate_sets import IBM_BASIS_GATES
from tessera.backends.decomposition_maps import IBM_DECOMP_MAP

BACKEND_REGISTRY = {
    "IBM": {
        "basis_gates": IBM_BASIS_GATES,
        "decomp_map": IBM_DECOMP_MAP,
        "coupling_map": "IBM_DEFAULT"
    }
    # Add new backend registrations here
}