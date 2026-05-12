from tessera.backends.basis_gate_sets import IBM_BASIS_GATES, IONQ_BASIS_GATES, RIGETTI_BASIS_GATES

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

def test_ionq_basis_gates_contains_expected():
    for gate in ("rx", "ry", "rz", "cx"):
        assert gate in IONQ_BASIS_GATES

def test_ionq_basis_gates_excludes_non_basis():
    for gate in ("h", "x", "sx", "u", "cz"):
        assert gate not in IONQ_BASIS_GATES

def test_rigetti_basis_gates_contains_expected():
    for gate in ("rx", "rz", "cz"):
        assert gate in RIGETTI_BASIS_GATES

def test_rigetti_basis_gates_excludes_non_basis():
    for gate in ("h", "cx", "ry", "sx", "u"):
        assert gate not in RIGETTI_BASIS_GATES