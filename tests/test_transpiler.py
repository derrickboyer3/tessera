from qiskit import QuantumCircuit
from tessera.transpiler import TesseraTranspiler
from tessera.backends.basis_gate_sets import IBM_BASIS_GATES
from tessera.hardware.coupling_map import TesseraCouplingMap

BASIS_PLUS_MEASURE = IBM_BASIS_GATES | {"measure", "swap"}

def make_simple_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def make_coupling_map():
    return TesseraCouplingMap(2, [(0, 1)])

def test_execute_returns_qiskit_circuit():
    qc = make_simple_circuit()
    result = TesseraTranspiler(qc, make_coupling_map()).execute()
    assert result is not None

def test_output_only_contains_basis_gates():
    qc = make_simple_circuit()
    result = TesseraTranspiler(qc, make_coupling_map()).execute()
    for ins in result.data:
        assert ins.operation.name in BASIS_PLUS_MEASURE

def test_default_backend_is_ibm():
    qc = make_simple_circuit()
    t = TesseraTranspiler(qc, make_coupling_map())
    assert t.backend == "IBM"

def test_debug_off_by_default():
    qc = make_simple_circuit()
    t = TesseraTranspiler(qc, make_coupling_map())
    assert t.debug_on == False

def test_qubit_count_preserved():
    qc = make_simple_circuit()
    result = TesseraTranspiler(qc, make_coupling_map()).execute()
    assert result.num_qubits == qc.num_qubits
    assert result.num_clbits == qc.num_clbits

def test_basic_with_debug():
    qc = make_simple_circuit()
    result = TesseraTranspiler(qc, make_coupling_map(), debug_on=True).execute()
    assert result is not None

def test_strict_defaults_to_true():
    qc = make_simple_circuit()
    t = TesseraTranspiler(qc, make_coupling_map())
    assert t.strict == True

def test_epsilon_defaults_to_1e9():
    qc = make_simple_circuit()
    t = TesseraTranspiler(qc, make_coupling_map())
    assert t.epsilon == 1e-9

def test_custom_strict_false():
    qc = make_simple_circuit()
    t = TesseraTranspiler(qc, make_coupling_map(), strict=False)
    assert t.strict == False

def test_custom_epsilon():
    qc = make_simple_circuit()
    t = TesseraTranspiler(qc, make_coupling_map(), epsilon=1e-6)
    assert t.epsilon == 1e-6

def test_barriers_removed_after_execute():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.barrier()
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    result = TesseraTranspiler(qc, make_coupling_map()).execute()
    for ins in result.data:
        assert ins.operation.name != "barrier"