'''
    Tests for dense_layout
    ----------------------
    Covers the dense layout algorithm — greedy interaction-frequency placement
    of logical qubits onto physical qubits.
'''
import pytest
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.layouts.dense import dense_layout


def make_coupling_map():
    # Linear: 0->1->2->3->4 (directed)
    return TesseraCouplingMap(5, [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 3)])


def test_too_many_qubits_raises():
    cm = TesseraCouplingMap(2, [(0, 1)])
    with pytest.raises(ValueError, match="too many qubits"):
        dense_layout(TesseraCircuit(3, 0, []), cm)


def test_all_qubits_assigned():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
    ])
    layout = dense_layout(circuit, make_coupling_map())
    assert set(layout.keys()) == {0, 1, 2}


def test_no_duplicate_physical_qubits():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
    ])
    layout = dense_layout(circuit, make_coupling_map())
    physical = list(layout.values())
    assert len(physical) == len(set(physical))


def test_frequent_pair_placed_close():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    cm = make_coupling_map()
    layout = dense_layout(circuit, cm)
    assert cm.distance(layout[0], layout[2]) == 1


def test_no_interactions_still_assigns_all():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("x", [0], [], []),
        TesseraInstruction("x", [1], [], []),
        TesseraInstruction("x", [2], [], []),
    ])
    layout = dense_layout(circuit, make_coupling_map())
    assert set(layout.keys()) == {0, 1, 2}


def test_empty_circuit_assigns_all():
    layout = dense_layout(TesseraCircuit(3, 0, []), make_coupling_map())
    assert set(layout.keys()) == {0, 1, 2}


def test_three_qubit_gate_interactions():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("ccx", [0, 1, 2], [], []),
    ])
    layout = dense_layout(circuit, make_coupling_map())
    assert set(layout.keys()) == {0, 1, 2}


def test_find_closest_pair_skips_unreachable():
    cm = TesseraCouplingMap(4, [])  # fully disconnected
    circuit = TesseraCircuit(2, 0, [TesseraInstruction("cx", [0, 1], [], [])])
    layout = dense_layout(circuit, cm)
    assert set(layout.keys()) == {0, 1}


def test_find_closest_free_skips_unreachable():
    # Two disconnected pairs
    cm = TesseraCouplingMap(4, [(0, 1), (2, 3)])
    circuit = TesseraCircuit(2, 0, [TesseraInstruction("cx", [0, 1], [], [])])
    layout = dense_layout(circuit, cm)
    assert set(layout.keys()) == {0, 1}


def test_q1_assigned_first_q0_placed_after():
    # Force the "elif q1 in assigned and q0 not in assigned" branch
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    layout = dense_layout(circuit, make_coupling_map())
    assert set(layout.keys()) == {0, 1, 2}


def test_find_closest_free_unreachable_branch():
    cm = TesseraCouplingMap(4, [(0, 1), (2, 3)])
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    layout = dense_layout(circuit, cm)
    assert set(layout.keys()) == {0, 1, 2}
