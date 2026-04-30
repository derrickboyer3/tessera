from tessera.backends.decomposition_maps import IBM_DECOMP_MAP
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