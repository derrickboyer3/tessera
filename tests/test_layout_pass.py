'''
    Tests for LayoutPass
    --------------------
    Covers string-based algorithm resolution, callable injection, validation,
    and layout application to the output circuit.
'''
import pytest
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.passes.layout_pass import LayoutPass


def make_circuit():
    return TesseraCircuit(3, 0, [TesseraInstruction("cx", [0, 1], [], [])])


def make_coupling_map():
    return TesseraCouplingMap(4, [(0, 1), (1, 2), (2, 3)])


# Resolution

def test_default_algorithm_is_dense():
    p = LayoutPass(make_coupling_map())
    result = p.run(make_circuit())
    assert result.layout
    assert set(result.layout.keys()) == {0, 1, 2}


def test_string_algorithm_trivial():
    p = LayoutPass(make_coupling_map(), "trivial")
    result = p.run(make_circuit())
    assert result.layout == {0: 0, 1: 1, 2: 2}


def test_string_algorithm_dense():
    p = LayoutPass(make_coupling_map(), "dense")
    result = p.run(make_circuit())
    assert set(result.layout.keys()) == {0, 1, 2}


def test_string_algorithm_sabre():
    p = LayoutPass(make_coupling_map(), "sabre")
    result = p.run(make_circuit())
    assert set(result.layout.keys()) == {0, 1, 2}


def test_callable_algorithm_used_directly():
    sentinel_layout = {0: 3, 1: 2, 2: 1}

    def custom(circuit, coupling_map):
        return dict(sentinel_layout)

    p = LayoutPass(make_coupling_map(), custom)
    result = p.run(make_circuit())
    assert result.layout == sentinel_layout


# Validation

def test_unknown_string_algorithm_raises():
    with pytest.raises(ValueError, match="Unknown layout algorithm"):
        LayoutPass(make_coupling_map(), "not_a_real_algorithm")


def test_non_string_non_callable_raises():
    with pytest.raises(ValueError, match="must be a string or callable"):
        LayoutPass(make_coupling_map(), 123)


# Preservation

def test_preserves_instructions():
    instructions = [TesseraInstruction("cx", [0, 1], [], [])]
    circuit = TesseraCircuit(2, 0, instructions)
    result = LayoutPass(make_coupling_map(), "trivial").run(circuit)
    assert result.instructions == instructions


def test_preserves_num_qubits():
    result = LayoutPass(make_coupling_map(), "trivial").run(TesseraCircuit(3, 0, []))
    assert result.num_qubits == 3


def test_preserves_num_clbits():
    result = LayoutPass(make_coupling_map(), "trivial").run(TesseraCircuit(2, 4, []))
    assert result.num_clbits == 4
