'''
    Tests for sabre_route
    ---------------------
    Covers the SABRE whole-circuit routing algorithm and its helpers
    (front layer, executability, candidate swaps, extended set, heuristic).
'''
import pytest
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.routing.sabre import (
    sabre_route,
    compute_front_layer,
    is_executable,
    translate,
    candidate_swaps,
    compute_extended_set,
    heuristic_score,
)


def make_linear_map():
    return TesseraCouplingMap(4, [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2)])


# Top-level

def test_no_layout_raises():
    circuit = TesseraCircuit(2, 0, [TesseraInstruction("cx", [0, 1], [], [])])
    with pytest.raises(ValueError, match="No layout found"):
        sabre_route(circuit, make_linear_map())


def test_adjacent_two_qubit_gate_passthrough():
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
    ], layout={0: 0, 1: 1})
    result = sabre_route(circuit, make_linear_map())
    assert len(result.instructions) == 1
    assert result.instructions[0].name == "cx"


def test_single_qubit_translates_via_layout():
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("x", [0], [], []),
    ], layout={0: 3, 1: 2})
    result = sabre_route(circuit, make_linear_map())
    assert result.instructions[0].qubits == [3]


def test_measure_translates_via_layout():
    circuit = TesseraCircuit(2, 1, [
        TesseraInstruction("measure", [0], [0], []),
    ], layout={0: 2, 1: 3})
    result = sabre_route(circuit, make_linear_map())
    assert result.instructions[0].name == "measure"
    assert result.instructions[0].qubits == [2]


def test_non_adjacent_two_qubit_inserts_swap():
    circuit = TesseraCircuit(4, 0, [
        TesseraInstruction("cx", [0, 3], [], []),
    ], layout={0: 0, 1: 1, 2: 2, 3: 3})
    result = sabre_route(circuit, make_linear_map())
    names = [ins.name for ins in result.instructions]
    assert "swap" in names
    assert "cx" in names


def test_three_qubit_gate_raises():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("ccx", [0, 1, 2], [], []),
    ], layout={0: 0, 1: 1, 2: 2})
    with pytest.raises(ValueError, match="Decompose to 2-qubit gates"):
        sabre_route(circuit, make_linear_map())


def test_layout_preserved_on_output():
    circuit = TesseraCircuit(3, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
    ], layout={0: 0, 1: 1, 2: 2})
    result = sabre_route(circuit, make_linear_map())
    assert result.layout == {0: 0, 1: 1, 2: 2}


def test_sabre_routes_through_unmapped_qubit():
    # Sparse layout: 2-qubit circuit on a 4-qubit coupling map. Logical q0
    # and q1 are mapped to physical 0 and 2 — not adjacent. SABRE has to
    # route via physical 1, which is unmapped. The swap that pulls logical
    # q0 toward q1 lands on (mapped, unmapped) and exercises the elif log0
    # branch in the swap-update logic.
    cm = make_linear_map()
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("cx", [0, 1], [], []),
    ], layout={0: 0, 1: 2})
    result = sabre_route(circuit, cm)
    names = [ins.name for ins in result.instructions]
    assert "swap" in names
    assert "cx" in names


# Helpers — front layer

def test_front_layer_empty_on_empty_remaining():
    assert compute_front_layer([]) == []


def test_front_layer_first_instruction_always_included():
    instructions = [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("cx", [1, 2], [], []),
    ]
    front = compute_front_layer(instructions)
    assert instructions[0] in front


def test_front_layer_excludes_blocked_instructions():
    instructions = [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("cx", [1, 2], [], []),  # blocked: shares q1
    ]
    front = compute_front_layer(instructions)
    assert instructions[1] not in front


def test_front_layer_includes_independent_instructions():
    instructions = [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("cx", [2, 3], [], []),  # disjoint qubits
    ]
    front = compute_front_layer(instructions)
    assert len(front) == 2


# Helpers — is_executable

def test_is_executable_measure_is_always_true():
    ins = TesseraInstruction("measure", [0], [0], [])
    assert is_executable(ins, {0: 0}, make_linear_map())


def test_is_executable_barrier_is_always_true():
    ins = TesseraInstruction("barrier", [0, 1], [], [])
    assert is_executable(ins, {0: 0, 1: 1}, make_linear_map())


def test_is_executable_single_qubit_is_always_true():
    ins = TesseraInstruction("x", [0], [], [])
    assert is_executable(ins, {0: 3}, make_linear_map())


def test_is_executable_adjacent_two_qubit_true():
    ins = TesseraInstruction("cx", [0, 1], [], [])
    assert is_executable(ins, {0: 0, 1: 1}, make_linear_map())


def test_is_executable_non_adjacent_two_qubit_false():
    ins = TesseraInstruction("cx", [0, 1], [], [])
    assert not is_executable(ins, {0: 0, 1: 3}, make_linear_map())


def test_is_executable_three_qubit_raises():
    ins = TesseraInstruction("ccx", [0, 1, 2], [], [])
    with pytest.raises(ValueError, match="Decompose to 2-qubit gates"):
        is_executable(ins, {0: 0, 1: 1, 2: 2}, make_linear_map())


# Helpers — translate

def test_translate_swaps_qubit_indices():
    ins = TesseraInstruction("cx", [0, 1], [], [])
    translated = translate(ins, {0: 3, 1: 2})
    assert translated.qubits == [3, 2]
    assert translated.name == "cx"


# Helpers — candidate swaps

def test_candidate_swaps_empty_when_no_two_qubit_gates():
    front = [TesseraInstruction("x", [0], [], [])]
    assert candidate_swaps(front, {0: 0}, make_linear_map()) == []


def test_candidate_swaps_includes_neighbors():
    front = [TesseraInstruction("cx", [0, 1], [], [])]
    swaps = candidate_swaps(front, {0: 0, 1: 1}, make_linear_map())
    # Physical 0 and 1 are involved; expect swaps along their adjacent edges
    assert len(swaps) > 0
    for swap in swaps:
        assert 0 in swap or 1 in swap


# Helpers — extended set

def test_extended_set_skips_front_layer_gates():
    remaining = [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("cx", [0, 2], [], []),
        TesseraInstruction("cx", [1, 3], [], []),
    ]
    front = [remaining[0]]
    ext = compute_extended_set(remaining, front, 10)
    assert remaining[0] not in ext


def test_extended_set_respects_size_limit():
    remaining = [TesseraInstruction("cx", [i, i + 1], [], []) for i in range(10)]
    front = [remaining[0]]
    ext = compute_extended_set(remaining, front, 3)
    assert len(ext) <= 3


def test_extended_set_only_includes_two_qubit_gates():
    remaining = [
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("x", [0], [], []),         # single-qubit, skipped
        TesseraInstruction("cx", [2, 3], [], []),
    ]
    front = [remaining[0]]
    ext = compute_extended_set(remaining, front, 10)
    assert all(len(ins.qubits) == 2 for ins in ext)


# Helpers — heuristic score

def test_heuristic_score_lower_when_swap_helps():
    cm = make_linear_map()
    front = [TesseraInstruction("cx", [0, 1], [], [])]
    extended = []
    mapping = {0: 0, 1: 2}  # logical 0 at physical 0, logical 1 at physical 2 — distance 2
    # Swap (1, 2) brings logical 1 to physical 1, making q0/q1 adjacent.
    score_helpful = heuristic_score((1, 2), front, extended, mapping, cm, 0.5)
    # Swap (2, 3) does nothing useful for this front.
    score_unhelpful = heuristic_score((2, 3), front, extended, mapping, cm, 0.5)
    assert score_helpful < score_unhelpful


def test_heuristic_score_handles_empty_layers():
    cm = make_linear_map()
    mapping = {0: 0, 1: 1}
    score = heuristic_score((0, 1), [], [], mapping, cm, 0.5)
    assert score == 0


def test_heuristic_score_skips_non_two_qubit_gates_in_front():
    # Single-qubit and measurement gates in the front shouldn't contribute
    # to the layer cost — they have nothing to do with routing distance.
    cm = make_linear_map()
    mapping = {0: 0, 1: 1}
    front = [
        TesseraInstruction("x", [0], [], []),
        TesseraInstruction("measure", [1], [0], []),
    ]
    score = heuristic_score((0, 1), front, [], mapping, cm, 0.5)
    assert score == 0
