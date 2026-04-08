from circuit import TesseraCircuit
from instruction import TesseraInstruction
from hardware.coupling_map import TesseraCouplingMap
from passes.dense_layout_pass import DenseLayoutPass
import pytest

def make_coupling_map():
    # Linear: 0->1->2->3->4
    return TesseraCouplingMap(5, [(0,1), (1,2), (2,3), (3,4)])

def test_too_many_qubits_raises():
    cm = TesseraCouplingMap(2, [(0,1)])
    circuit = TesseraCircuit(3, 0, [])
    with pytest.raises(ValueError, match="too many qubits"):
        DenseLayoutPass(cm).run(circuit)

def test_all_qubits_assigned():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
    ])
    result = DenseLayoutPass(make_coupling_map()).run(circuit)
    assert set(result.layout.keys()) == {0, 1, 2}

def test_no_duplicate_physical_qubits():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
    ])
    result = DenseLayoutPass(make_coupling_map()).run(circuit)
    physical = list(result.layout.values())
    assert len(physical) == len(set(physical))

def test_frequent_pair_placed_close():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    cm = make_coupling_map()
    result = DenseLayoutPass(cm).run(circuit)
    p0 = result.layout[0]
    p2 = result.layout[2]
    assert cm.distance(p0, p2) == 1

def test_preserves_instructions():
    instructions = [TesseraInstruction("cx", [0, 1], [], [])]
    circuit = TesseraCircuit(2, 0, instructions)
    result = DenseLayoutPass(make_coupling_map()).run(circuit)
    assert result.instructions == instructions

def test_preserves_num_qubits():
    circuit = TesseraCircuit(3, 0, [])
    result = DenseLayoutPass(make_coupling_map()).run(circuit)
    assert result.num_qubits == 3

def test_preserves_num_clbits():
    circuit = TesseraCircuit(3, 2, [])
    result = DenseLayoutPass(make_coupling_map()).run(circuit)
    assert result.num_clbits == 2

def test_no_interactions_still_assigns_all():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("x", [0], [], []),
        TesseraInstruction("x", [1], [], []),
        TesseraInstruction("x", [2], [], []),
    ])
    result = DenseLayoutPass(make_coupling_map()).run(circuit)
    assert set(result.layout.keys()) == {0, 1, 2}

def test_empty_circuit_assigns_all():
    circuit = TesseraCircuit(3, 0, [])
    result = DenseLayoutPass(make_coupling_map()).run(circuit)
    assert set(result.layout.keys()) == {0, 1, 2}

def test_three_qubit_gate_interactions():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("ccx", [0, 1, 2], [], []),
    ])
    result = DenseLayoutPass(make_coupling_map()).run(circuit)
    assert set(result.layout.keys()) == {0, 1, 2}

def test_find_closest_free_skips_unreachable():
    # Disconnected map where some qubits have no path between them
    cm = TesseraCouplingMap(4, [(0,1), (2,3)])  # two disconnected pairs
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    result = DenseLayoutPass(cm).run(circuit)
    assert set(result.layout.keys()) == {0, 1}

def test_find_closest_pair_skips_unreachable():
    # Fully disconnected map — no edges at all
    cm = TesseraCouplingMap(4, [])
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    result = DenseLayoutPass(cm).run(circuit)
    assert set(result.layout.keys()) == {0, 1}

def test_q1_assigned_first_q0_placed_after():
    # Force the elif q1 in assigned and q0 not in assigned branch
    # by having q1 appear in a high frequency pair first
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    result = DenseLayoutPass(make_coupling_map()).run(circuit)
    assert set(result.layout.keys()) == {0, 1, 2}
    p0 = result.layout[0]
    p1 = result.layout[1]
    assert make_coupling_map().distance(p1, p0) <= 2

def test_find_closest_free_with_unreachable_qubits():
    # q0 gets placed on physical qubit 0, but physical qubits 2 and 3
    # are unreachable from 0 in a directed graph
    cm = TesseraCouplingMap(4, [(0,1), (2,3)])
    # Force q1 to be assigned first by making (1,2) interact most
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [1, 2], [], []),
        TesseraInstruction("cx", [0, 1], [], []),
    ])
    result = DenseLayoutPass(cm).run(circuit)
    assert set(result.layout.keys()) == {0, 1, 2}