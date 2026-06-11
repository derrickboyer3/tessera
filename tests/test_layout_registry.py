'''
    Tests for LAYOUT_REGISTRY
    -------------------------
    Covers registry contents, callable shapes, and signature contract.
'''
from tessera.layouts.layout_registry import LAYOUT_REGISTRY
from tessera.layouts.dense import dense_layout
from tessera.layouts.sabre import sabre_layout
from tessera.layouts.trivial import trivial_layout
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.hardware.coupling_map import TesseraCouplingMap


def make_circuit():
    return TesseraCircuit(3, 0, [TesseraInstruction("cx", [0, 1], [], [])])


def make_coupling_map():
    return TesseraCouplingMap(4, [(0, 1), (1, 2), (2, 3)])


def test_registry_contains_dense():
    assert "dense" in LAYOUT_REGISTRY


def test_registry_contains_sabre():
    assert "sabre" in LAYOUT_REGISTRY


def test_registry_contains_trivial():
    assert "trivial" in LAYOUT_REGISTRY


def test_dense_entry_is_dense_layout():
    assert LAYOUT_REGISTRY["dense"] is dense_layout


def test_sabre_entry_is_sabre_layout():
    assert LAYOUT_REGISTRY["sabre"] is sabre_layout


def test_trivial_entry_is_trivial_layout():
    assert LAYOUT_REGISTRY["trivial"] is trivial_layout


def test_all_entries_are_callable():
    for fn in LAYOUT_REGISTRY.values():
        assert callable(fn)


def test_all_entries_return_dict():
    for name, fn in LAYOUT_REGISTRY.items():
        result = fn(make_circuit(), make_coupling_map())
        assert isinstance(result, dict), f"{name} did not return a dict"
        assert all(isinstance(k, int) and isinstance(v, int) for k, v in result.items())
