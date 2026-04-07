'''
    Tessera Backend Registry
    ------------------------
    Central registry mapping backend names to their corresponding basis gate sets
    and decomposition maps. When adding a new backend, import its basis gate set
    and decomposition map and add a new entry here. No other files need to change.
'''
from backends.basis_gate_sets import IBM_BASIS_GATES
from backends.decomposition_maps import IBM_DECOMP_MAP

BACKEND_REGISTRY = {
    "IBM": {
        "basis_gates": IBM_BASIS_GATES,
        "decomp_map": IBM_DECOMP_MAP
    }
    # Add new backend registrations here
}