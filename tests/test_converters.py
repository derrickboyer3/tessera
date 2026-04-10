from qiskit import QuantumCircuit
from converters import from_qiskit, to_qiskit
import pytest

def make_test_circuit():
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 2)
    qc.h(1)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

def test_from_qiskit_qubit_count():
    tc = from_qiskit(make_test_circuit())
    assert tc.num_qubits == 3

def test_from_qiskit_clbit_count():
    tc = from_qiskit(make_test_circuit())
    assert tc.num_clbits == 3

def test_from_qiskit_instruction_count():
    tc = from_qiskit(make_test_circuit())
    assert len(tc.instructions) == 6

def test_from_qiskit_gate_names():
    tc = from_qiskit(make_test_circuit())
    names = [i.name for i in tc.instructions]
    assert names == ["h", "cx", "h", "measure", "measure", "measure"]

def test_round_trip():
    qc = make_test_circuit()
    tc = from_qiskit(qc)
    qc2 = to_qiskit(tc)
    assert qc2.num_qubits == qc.num_qubits
    assert qc2.num_clbits == qc.num_clbits
    assert len(qc2.data) == len(qc.data)

def test_unknown_gate_raises():
    from converters import gate_from_name
    with pytest.raises(ValueError, match="Unknown gate"):
        gate_from_name("fake_gate", [])

def test_to_qiskit_barrier():
    from qiskit import QuantumCircuit
    from converters import to_qiskit
    from circuit import TesseraCircuit
    from instruction import TesseraInstruction
    tc = TesseraCircuit(2, 0, [
        TesseraInstruction("barrier", [0, 1]),
    ])
    qc = to_qiskit(tc)
    assert any(ins.operation.name == "barrier" for ins in qc.data)