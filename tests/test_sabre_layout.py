'''
    Tests for sabre_layout
    ----------------------
    Covers the SABRE layout discovery algorithm — forward/backward trial
    routing produces a valid initial mapping that minimizes routing distance.
'''
import pytest
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.layouts.sabre import sabre_layout, _trial_route_final_mapping


def make_coupling_map():
    return TesseraCouplingMap(4, [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2)])


def test_too_many_qubits_raises():
    cm = TesseraCouplingMap(2, [(0, 1)])
    with pytest.raises(ValueError, match="too many qubits"):
        sabre_layout(TesseraCircuit(3, 0, []), cm)


def test_all_qubits_assigned():
    circuit = TesseraCircuit(4, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    layout = sabre_layout(circuit, make_coupling_map())
    assert set(layout.keys()) == {0, 1, 2, 3}


def test_layout_is_a_permutation():
    circuit = TesseraCircuit(4, 0, [
        TesseraInstruction("cx", [0, 3], [], []),
    ])
    layout = sabre_layout(circuit, make_coupling_map())
    assert set(layout.values()) == {0, 1, 2, 3}


def test_layout_brings_frequent_pair_close():
    # q0 and q3 interact 3 times — trivial leaves them 3 hops apart.
    # SABRE should bring them closer.
    circuit = TesseraCircuit(4, 0, [
        TesseraInstruction("cx", [0, 3], [], []),
        TesseraInstruction("cx", [0, 3], [], []),
        TesseraInstruction("cx", [0, 3], [], []),
    ])
    cm = make_coupling_map()
    layout = sabre_layout(circuit, cm)
    assert cm.distance(layout[0], layout[3]) < 3


def test_empty_circuit_returns_trivial_mapping():
    # No instructions -> no swap decisions to refine the mapping ->
    # should return the trivial starting mapping unchanged.
    layout = sabre_layout(TesseraCircuit(4, 0, []), make_coupling_map())
    assert layout == {0: 0, 1: 1, 2: 2, 3: 3}


def test_single_qubit_only_returns_trivial_mapping():
    circuit = TesseraCircuit(4, 0, [
        TesseraInstruction("x", [0], [], []),
        TesseraInstruction("h", [2], [], []),
    ])
    layout = sabre_layout(circuit, make_coupling_map())
    assert layout == {0: 0, 1: 1, 2: 2, 3: 3}


# Helper

def test_trial_route_replays_swaps_correctly():
    # Single swap in the routed output should swap the mapping accordingly.
    cm = make_coupling_map()
    circuit = TesseraCircuit(4, 0, [
        TesseraInstruction("cx", [0, 2], [], []),
    ], layout={0: 0, 1: 1, 2: 2, 3: 3})
    final = _trial_route_final_mapping(circuit, cm, {0: 0, 1: 1, 2: 2, 3: 3})
    # After routing cx(0,2), the mapping should have shifted so q0 and q2 ended adjacent
    assert set(final.values()) == {0, 1, 2, 3}
    assert cm.distance(final[0], final[2]) == 1


def test_trial_route_handles_sparse_initial_mapping():
    # 2-qubit circuit on a 4-qubit coupling map with sparse initial mapping —
    # logical q0 at physical 0, logical q1 at physical 2. Routing has to swap
    # through unmapped physical 1. The replay-swaps logic exercises the
    # elif log0 branch when handling a (mapped, unmapped) swap.
    cm = make_coupling_map()
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    final = _trial_route_final_mapping(circuit, cm, {0: 0, 1: 2})
    # Both logical qubits should still be present in the final mapping
    assert 0 in final and 1 in final
    # And mapped to distinct physical qubits
    assert final[0] != final[1]
