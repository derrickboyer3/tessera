'''
    Tests for DenseLayoutPass (Deprecated Shim)
    -------------------------------------------
    DenseLayoutPass is now a thin backwards-compatibility shim that delegates
    to LayoutPass(coupling_map, "dense"). These tests confirm the deprecation
    warning fires and the behavior is preserved.

    Detailed algorithm tests live in test_dense.py against the standalone
    dense_layout function.
'''
import warnings
import pytest
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.passes.dense_layout_pass import DenseLayoutPass


def make_coupling_map():
    return TesseraCouplingMap(5, [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 3)])


def test_construction_emits_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="DenseLayoutPass is deprecated"):
        DenseLayoutPass(make_coupling_map())


def test_still_produces_valid_layout():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
    ])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = DenseLayoutPass(make_coupling_map()).run(circuit)
    assert set(result.layout.keys()) == {0, 1, 2}
    assert len(set(result.layout.values())) == 3   # no duplicates


def test_delegates_to_dense_algorithm():
    # Confirm output matches LayoutPass(..., "dense") on the same input.
    from tessera.passes.layout_pass import LayoutPass
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        deprecated_result = DenseLayoutPass(make_coupling_map()).run(circuit)
    layout_pass_result = LayoutPass(make_coupling_map(), "dense").run(circuit)
    assert deprecated_result.layout == layout_pass_result.layout
