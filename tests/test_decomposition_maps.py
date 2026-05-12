from tessera.backends.decomposition_maps import IBM_DECOMP_MAP, IONQ_DECOMP_MAP, RIGETTI_DECOMP_MAP
from tessera.instruction import TesseraInstruction
import numpy as np
pi = np.pi

def test_all_expected_gates_present():
    expected = ["h", "y", "z", "s", "sdg", "t", "tdg", "p", "rx", "ry", "cz", "cy", "swap", "cp", "ccx"]
    for gate in expected:
        assert gate in IBM_DECOMP_MAP, f"Missing decomposition for '{gate}'"

def test_static_decomps_are_lists():
    static_gates = ["h", "y", "z", "s", "sdg", "t", "tdg", "cz", "cy", "swap", "ccx"]
    for gate in static_gates:
        assert isinstance(IBM_DECOMP_MAP[gate], list), f"'{gate}' should be a list"

def test_param_decomps_are_callable():
    param_gates = ["p", "rx", "ry", "cp"]
    for gate in param_gates:
        assert callable(IBM_DECOMP_MAP[gate]), f"'{gate}' should be callable"

def test_h_decomposes_to_correct_gates():
    decomp = IBM_DECOMP_MAP["h"]
    assert decomp[0].name == "rz"
    assert decomp[1].name == "sx"
    assert decomp[2].name == "rz"

def test_swap_decomposes_to_three_cx():
    decomp = IBM_DECOMP_MAP["swap"]
    assert len(decomp) == 3
    assert all(g.name == "cx" for g in decomp)

def test_p_lambda_returns_rz():
    decomp = IBM_DECOMP_MAP["p"]([pi / 2])
    assert len(decomp) == 1
    assert decomp[0].name == "rz"
    assert decomp[0].params[0] == pi / 2

def test_ionq_all_expected_gates_present():
    expected = ["h", "x", "y", "z", "s", "sdg", "t", "tdg", "sx", "p", "u", "cz", "cy", "swap", "cp", "ccx"]
    for gate in expected:
        assert gate in IONQ_DECOMP_MAP, f"Missing: '{gate}'"

def test_ionq_rx_ry_not_in_decomp_map():
    assert "rx" not in IONQ_DECOMP_MAP
    assert "ry" not in IONQ_DECOMP_MAP

def test_ionq_x_decomposes_to_rx():
    decomp = IONQ_DECOMP_MAP["x"]
    assert len(decomp) == 1
    assert decomp[0].name == "rx"

def test_ionq_u_lambda_uses_all_params():
    decomp = IONQ_DECOMP_MAP["u"]([1.0, 2.0, 3.0])
    assert [i.name for i in decomp] == ["rz", "ry", "rz"]
    assert decomp[0].params[0] == 2.0
    assert decomp[1].params[0] == 1.0
    assert decomp[2].params[0] == 3.0

def test_rigetti_all_expected_gates_present():
    expected = ["h", "x", "y", "z", "s", "sdg", "t", "tdg", "sx", "ry", "p", "u", "cx", "cy", "swap", "cp", "ccx"]
    for gate in expected:
        assert gate in RIGETTI_DECOMP_MAP, f"Missing: '{gate}'"

def test_rigetti_cx_decomposes_to_cz():
    from tessera.backends.basis_gate_sets import RIGETTI_BASIS_GATES
    decomp = RIGETTI_DECOMP_MAP["cx"]
    assert any(i.name == "cz" for i in decomp)
    assert all(i.name in RIGETTI_BASIS_GATES for i in decomp)

def test_rigetti_ry_uses_param():
    decomp = RIGETTI_DECOMP_MAP["ry"]([pi / 3])
    rx_gates = [i for i in decomp if i.name == "rx"]
    assert len(rx_gates) == 1
    assert rx_gates[0].params[0] == pi / 3