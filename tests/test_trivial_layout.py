'''
    Tests for trivial_layout
    ------------------------
    Covers the trivial layout algorithm — direct logical->physical mapping
    with no topology awareness.
'''
import pytest
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.layouts.trivial import trivial_layout


def make_circuit(num_qubits):
    return TesseraCircuit(num_qubits, 0, [
        TesseraInstruction("cx", [0, 1], [], [])
    ])


def make_coupling_map():
    return TesseraCouplingMap(4, [(0, 1), (1, 2), (2, 3)])


def test_trivial_layout_correct_mapping():
    layout = trivial_layout(make_circuit(3), make_coupling_map())
    assert layout == {0: 0, 1: 1, 2: 2}


def test_trivial_layout_exact_qubit_count():
    layout = trivial_layout(make_circuit(4), make_coupling_map())
    assert layout == {0: 0, 1: 1, 2: 2, 3: 3}


def test_trivial_layout_too_many_qubits_raises():
    with pytest.raises(ValueError, match="too many qubits"):
        trivial_layout(make_circuit(5), make_coupling_map())


def test_trivial_layout_empty_layout_on_zero_qubits():
    layout = trivial_layout(TesseraCircuit(0, 0, []), make_coupling_map())
    assert layout == {}
