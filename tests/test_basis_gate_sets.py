from tessera.backends.basis_gate_sets import IBM_BASIS_GATES

def test_ibm_basis_gates_contains_expected():
    assert "cx" in IBM_BASIS_GATES
    assert "rz" in IBM_BASIS_GATES
    assert "sx" in IBM_BASIS_GATES
    assert "x" in IBM_BASIS_GATES
    assert "u" in IBM_BASIS_GATES

def test_ibm_basis_gates_excludes_non_basis():
    assert "h" not in IBM_BASIS_GATES
    assert "y" not in IBM_BASIS_GATES
    assert "swap" not in IBM_BASIS_GATES
    assert "ccx" not in IBM_BASIS_GATES