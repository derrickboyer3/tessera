from circuit import TesseraCircuit
from instruction import TesseraInstruction
from hardware.coupling_map import TesseraCouplingMap
from passes.trivial_pass import TrivialPass
import pytest

def make_circuit(num_qubits):
    return TesseraCircuit(num_qubits, 0, [
        TesseraInstruction("cx", [0, 1], [], [])
    ])

def make_coupling_map():
    return TesseraCouplingMap(4, [(0,1), (1,2), (2,3)])

def test_trivial_layout_correct_mapping():
    circuit = make_circuit(3)
    result = TrivialPass(make_coupling_map()).run(circuit)
    assert result.layout == {0: 0, 1: 1, 2: 2}

def test_trivial_layout_preserves_instructions():
    circuit = make_circuit(2)
    result = TrivialPass(make_coupling_map()).run(circuit)
    assert result.instructions == circuit.instructions

def test_trivial_layout_preserves_num_qubits():
    circuit = make_circuit(2)
    result = TrivialPass(make_coupling_map()).run(circuit)
    assert result.num_qubits == 2

def test_trivial_layout_preserves_num_clbits():
    circuit = make_circuit(2)
    result = TrivialPass(make_coupling_map()).run(circuit)
    assert result.num_clbits == 0

def test_trivial_layout_exact_qubit_count():
    circuit = make_circuit(4)
    result = TrivialPass(make_coupling_map()).run(circuit)
    assert result.layout == {0: 0, 1: 1, 2: 2, 3: 3}

def test_trivial_layout_too_many_qubits_raises():
    circuit = make_circuit(5)
    with pytest.raises(ValueError, match="too many qubits"):
        TrivialPass(make_coupling_map()).run(circuit)

def test_trivial_layout_empty_layout_on_zero_qubits():
    circuit = TesseraCircuit(0, 0, [])
    result = TrivialPass(make_coupling_map()).run(circuit)
    assert result.layout == {}