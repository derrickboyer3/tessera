'''
    Tests for pairwise_route
    ------------------------
    Covers the shared SWAP-insertion engine used by BFS and A* routing
    strategies. Verifies passthrough behavior, layout translation, swap
    insertion, mapping updates, and error handling.
'''
import pytest
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.routing.pairwise import pairwise_route
from tessera.routing.bfs import bfs_path


def make_linear_map():
    return TesseraCouplingMap(4, [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2)])


def bfs_finder_for(cm):
    return lambda s, e: bfs_path(cm, s, e)


def test_no_layout_raises():
    circuit = TesseraCircuit(2, 0, [TesseraInstruction("cx", [0, 1], [], [])])
    with pytest.raises(ValueError, match="No layout found"):
        pairwise_route(circuit, make_linear_map(), bfs_finder_for(make_linear_map()))


def test_single_qubit_gate_translates_via_layout():
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("x", [0], [], []),
    ], layout={0: 2, 1: 3})
    cm = make_linear_map()
    result = pairwise_route(circuit, cm, bfs_finder_for(cm))
    assert result.instructions[0].name == "x"
    assert result.instructions[0].qubits == [2]


def test_measure_translates_via_layout():
    circuit = TesseraCircuit(2, 1, [
        TesseraInstruction("measure", [0], [0], []),
    ], layout={0: 2, 1: 3})
    cm = make_linear_map()
    result = pairwise_route(circuit, cm, bfs_finder_for(cm))
    assert result.instructions[0].name == "measure"
    assert result.instructions[0].qubits == [2]


def test_barrier_translates_via_layout():
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("barrier", [0, 1], [], []),
    ], layout={0: 2, 1: 3})
    cm = make_linear_map()
    result = pairwise_route(circuit, cm, bfs_finder_for(cm))
    assert result.instructions[0].name == "barrier"


def test_adjacent_two_qubit_gate_no_swap():
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
    ], layout={0: 0, 1: 1})
    cm = make_linear_map()
    result = pairwise_route(circuit, cm, bfs_finder_for(cm))
    assert len(result.instructions) == 1
    assert result.instructions[0].name == "cx"


def test_non_adjacent_two_qubit_gate_inserts_swap():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 2], [], []),
    ], layout={0: 0, 1: 1, 2: 2})
    cm = make_linear_map()
    result = pairwise_route(circuit, cm, bfs_finder_for(cm))
    names = [ins.name for ins in result.instructions]
    assert "swap" in names
    assert "cx" in names


def test_long_distance_inserts_multiple_swaps():
    circuit = TesseraCircuit(4, 0, [
        TesseraInstruction("cx", [0, 3], [], []),
    ], layout={0: 0, 1: 1, 2: 2, 3: 3})
    cm = make_linear_map()
    result = pairwise_route(circuit, cm, bfs_finder_for(cm))
    names = [ins.name for ins in result.instructions]
    assert names.count("swap") == 2


def test_three_qubit_gate_raises():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("ccx", [0, 1, 2], [], []),
    ], layout={0: 0, 1: 1, 2: 2})
    cm = make_linear_map()
    with pytest.raises(ValueError, match="Decompose to 2-qubit gates"):
        pairwise_route(circuit, cm, bfs_finder_for(cm))


def test_custom_path_finder_called():
    calls = []

    def custom(start, end):
        calls.append((start, end))
        return [start, start + 1, end]

    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 2], [], []),
    ], layout={0: 0, 1: 1, 2: 2})
    pairwise_route(circuit, make_linear_map(), custom)
    assert (0, 2) in calls


def test_layout_preserved_on_output():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
    ], layout={0: 0, 1: 1, 2: 2})
    cm = make_linear_map()
    result = pairwise_route(circuit, cm, bfs_finder_for(cm))
    assert result.layout == {0: 0, 1: 1, 2: 2}


def test_num_qubits_and_clbits_preserved():
    circuit = TesseraCircuit(3, 2, [
        TesseraInstruction("cx", [0, 1], [], []),
    ], layout={0: 0, 1: 1, 2: 2})
    cm = make_linear_map()
    result = pairwise_route(circuit, cm, bfs_finder_for(cm))
    assert result.num_qubits == 3
    assert result.num_clbits == 2


def test_pairwise_routes_through_unmapped_qubit():
    # Sparse layout: 2-qubit circuit on a 4-qubit coupling map. Logical q0
    # at physical 0, logical q1 at physical 2 — not adjacent, must route via
    # the unmapped physical qubit 1. The SWAP from physical 0 onto physical 1
    # lands on (mapped, unmapped), exercising the elif log_a branch in the
    # swap-update logic.
    cm = make_linear_map()
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
    ], layout={0: 0, 1: 2})
    result = pairwise_route(circuit, cm, bfs_finder_for(cm))
    names = [ins.name for ins in result.instructions]
    assert "swap" in names
    assert "cx" in names
