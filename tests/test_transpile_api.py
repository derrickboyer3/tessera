'''
    Tests for Tessera Top-Level Transpile Function
    ------------------------------------------------
    Covers happy path, coupling map resolution, validation errors,
    and debug mode. Tests all three coupling map input modes.
'''
import pytest
from qiskit import QuantumCircuit
from tessera.api.transpile import transpile
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.backends.coupling_maps import COUPLING_MAP_REGISTRY

# ── Helpers ───────────────────────────────────────────────────────────────────

def make_simple_circuit(num_qubits=2):
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc

# ── Happy Path ────────────────────────────────────────────────────────────────

def test_transpile_returns_qiskit_circuit():
    qc = make_simple_circuit()
    result = transpile(qc)
    assert result is not None

def test_transpile_default_backend_is_ibm():
    qc = make_simple_circuit()
    result = transpile(qc)
    assert result.num_qubits == qc.num_qubits

def test_transpile_with_explicit_backend():
    qc = make_simple_circuit()
    result = transpile(qc, backend="IBM")
    assert result is not None

def test_transpile_with_tessera_coupling_map():
    qc = make_simple_circuit()
    cm = TesseraCouplingMap(2, [(0, 1), (1, 0)])
    result = transpile(qc, coupling_map=cm)
    assert result is not None

def test_transpile_with_string_coupling_map_key():
    qc = make_simple_circuit()
    result = transpile(qc, coupling_map="IBM_DEFAULT")
    assert result is not None

def test_transpile_with_brisbane_coupling_map():
    qc = make_simple_circuit()
    result = transpile(qc, coupling_map="IBM_BRISBANE")
    assert result is not None

def test_transpile_with_sherbrooke_coupling_map():
    qc = make_simple_circuit()
    result = transpile(qc, coupling_map="IBM_SHERBROOKE")
    assert result is not None

def test_transpile_qubit_count_preserved():
    qc = make_simple_circuit()
    result = transpile(qc)
    assert result.num_qubits == qc.num_qubits

def test_transpile_debug_on():
    qc = make_simple_circuit()
    result = transpile(qc, debug_on=True)
    assert result is not None

def test_transpile_strict_false():
    qc = make_simple_circuit()
    result = transpile(qc, strict=False)
    assert result is not None

def test_transpile_custom_epsilon():
    qc = make_simple_circuit()
    result = transpile(qc, epsilon=1e-6)
    assert result is not None

def test_transpile_none_coupling_map_uses_default():
    qc = make_simple_circuit()
    result_none = transpile(qc, coupling_map=None)
    result_default = transpile(qc, coupling_map="IBM_DEFAULT")
    assert result_none.num_qubits == result_default.num_qubits

# ── Validation Errors ─────────────────────────────────────────────────────────

def test_transpile_invalid_backend_raises():
    qc = make_simple_circuit()
    with pytest.raises(ValueError, match="BACKEND_REGISTRY"):
        transpile(qc, backend="FAKE_BACKEND")

def test_transpile_invalid_coupling_map_key_raises():
    qc = make_simple_circuit()
    with pytest.raises(ValueError, match="COUPLING_MAP_REGISTRY"):
        transpile(qc, coupling_map="FAKE_KEY")

def test_transpile_circuit_too_large_raises():
    qc = QuantumCircuit(100, 100)
    qc.h(0)
    qc.measure_all()
    cm = TesseraCouplingMap(2, [(0, 1), (1, 0)])
    with pytest.raises(ValueError, match="too big"):
        transpile(qc, coupling_map=cm)

def test_transpile_with_ionq_backend():
    qc = make_simple_circuit()
    result = transpile(qc, backend="IONQ")
    assert result is not None

def test_transpile_with_rigetti_backend():
    qc = make_simple_circuit()
    result = transpile(qc, backend="RIGETTI")
    assert result is not None

def test_transpile_ionq_with_forte_map():
    qc = make_simple_circuit()
    result = transpile(qc, backend="IONQ", coupling_map="IONQ_FORTE")
    assert result is not None

def test_transpile_rigetti_with_ankaa_9q_map():
    qc = make_simple_circuit()
    result = transpile(qc, backend="RIGETTI", coupling_map="RIGETTI_ANKAA_9Q")
    assert result is not None