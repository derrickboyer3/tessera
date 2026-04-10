'''
    Tests for MergeRotationsPass
    -----------------------------
    Covers strict and commutative modes for rotation gate merging.
    Tests happy path, edge cases, zero-angle dropping, and mixed circuit scenarios.
'''
import pytest
import math
from circuit import TesseraCircuit
from instruction import TesseraInstruction
from passes.merge_rotations_pass import MergeRotationsPass

# ── Helpers ───────────────────────────────────────────────────────────────────

def make_circuit(*instructions):
    return TesseraCircuit(num_qubits=3, num_clbits=0, instructions=list(instructions))

def ins(name, qubits, params=None):
    return TesseraInstruction(name=name, qubits=qubits, params=params or [])

# ── Strict Mode ───────────────────────────────────────────────────────────────

def test_strict_merges_adjacent_rz():
    circ = make_circuit(ins("rz", [0], [0.3]), ins("rz", [0], [0.5]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 1
    assert result.instructions[0].name == "rz"
    assert abs(result.instructions[0].params[0] - 0.8) < 1e-9

def test_strict_merges_adjacent_rx():
    circ = make_circuit(ins("rx", [0], [0.3]), ins("rx", [0], [0.5]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 1
    assert abs(result.instructions[0].params[0] - 0.8) < 1e-9

def test_strict_merges_adjacent_ry():
    circ = make_circuit(ins("ry", [0], [0.3]), ins("ry", [0], [0.5]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 1
    assert abs(result.instructions[0].params[0] - 0.8) < 1e-9

def test_strict_drops_zero_angle():
    circ = make_circuit(ins("rz", [0], [0.5]), ins("rz", [0], [-0.5]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert result.instructions == []

def test_strict_drops_near_zero_angle():
    circ = make_circuit(ins("rz", [0], [1e-10]), ins("rz", [0], [-1e-10]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert result.instructions == []

def test_strict_no_merge_different_qubits():
    circ = make_circuit(ins("rz", [0], [0.5]), ins("rz", [1], [0.5]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 2

def test_strict_no_merge_different_gate_types():
    circ = make_circuit(ins("rz", [0], [0.5]), ins("rx", [0], [0.5]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 2

def test_strict_no_merge_non_adjacent():
    circ = make_circuit(ins("rz", [0], [0.3]), ins("x", [1]), ins("rz", [0], [0.5]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 3

def test_strict_triple_rz_leaves_one_unmerged():
    circ = make_circuit(ins("rz", [0], [0.3]), ins("rz", [0], [0.3]), ins("rz", [0], [0.3]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 2
    assert abs(result.instructions[0].params[0] - 0.6) < 1e-9
    assert abs(result.instructions[1].params[0] - 0.3) < 1e-9

def test_strict_preserves_non_rotation_gates():
    circ = make_circuit(ins("x", [0]), ins("cx", [0, 1]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 2

def test_strict_preserves_layout_and_clbits():
    circ = TesseraCircuit(num_qubits=2, num_clbits=2, instructions=[ins("rz", [0], [0.3]), ins("rz", [0], [0.5])], layout={0: 1, 1: 2})
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 1
    assert result.layout == {0: 1, 1: 2}
    assert result.num_clbits == 2

def test_strict_empty_circuit():
    circ = make_circuit()
    result = MergeRotationsPass(strict=True).run(circ)
    assert result.instructions == []

def test_strict_single_gate_unchanged():
    circ = make_circuit(ins("rz", [0], [0.5]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 1
    assert abs(result.instructions[0].params[0] - 0.5) < 1e-9

def test_strict_custom_epsilon():
    circ = make_circuit(ins("rz", [0], [0.001]), ins("rz", [0], [-0.001]))
    result = MergeRotationsPass(strict=True, epsilon=0.01).run(circ)
    assert result.instructions == []

def test_strict_preserves_qubit_order_no_merge():
    circ = make_circuit(ins("rz", [0, 1], [0.5]), ins("rz", [1, 0], [0.5]))
    result = MergeRotationsPass(strict=True).run(circ)
    assert len(result.instructions) == 2

# ── Commutative Mode ──────────────────────────────────────────────────────────

def test_commutative_merges_adjacent():
    circ = make_circuit(ins("rz", [0], [0.3]), ins("rz", [0], [0.5]))
    result = MergeRotationsPass(strict=False).run(circ)
    assert len(result.instructions) == 1
    assert abs(result.instructions[0].params[0] - 0.8) < 1e-9

def test_commutative_merges_across_non_overlapping():
    circ = make_circuit(ins("rz", [0], [0.3]), ins("x", [1]), ins("rz", [0], [0.5]))
    result = MergeRotationsPass(strict=False).run(circ)
    assert len(result.instructions) == 2
    assert result.instructions[0].name == "rz"
    assert abs(result.instructions[0].params[0] - 0.8) < 1e-9
    assert result.instructions[1].name == "x"

def test_commutative_blocked_by_overlapping_gate():
    circ = make_circuit(ins("rz", [0], [0.3]), ins("x", [0]), ins("rz", [0], [0.5]))
    result = MergeRotationsPass(strict=False).run(circ)
    assert len(result.instructions) == 3

def test_commutative_drops_zero_across_non_overlapping():
    circ = make_circuit(ins("rz", [0], [0.5]), ins("x", [1]), ins("rz", [0], [-0.5]))
    result = MergeRotationsPass(strict=False).run(circ)
    assert len(result.instructions) == 1
    assert result.instructions[0].name == "x"

def test_commutative_no_merge_different_gate_types():
    circ = make_circuit(ins("rz", [0], [0.5]), ins("rx", [0], [0.5]))
    result = MergeRotationsPass(strict=False).run(circ)
    assert len(result.instructions) == 2

def test_commutative_preserves_layout():
    circ = TesseraCircuit(num_qubits=2, num_clbits=0, instructions=[ins("rz", [0], [0.3]), ins("x", [1]), ins("rz", [0], [0.5])], layout={0: 2, 1: 3})
    result = MergeRotationsPass(strict=False).run(circ)
    assert result.layout == {0: 2, 1: 3}

def test_commutative_empty_circuit():
    circ = make_circuit()
    result = MergeRotationsPass(strict=False).run(circ)
    assert result.instructions == []

def test_commutative_skips_already_merged_gate():
    circ = make_circuit(
        ins("rz", [1], [0.3]),
        ins("rz", [1], [0.3]),
        ins("rz", [0], [0.3]),
        ins("rz", [0], [0.3]),
    )
    result = MergeRotationsPass(strict=False).run(circ)
    assert len(result.instructions) == 2
    assert abs(result.instructions[0].params[0] - 0.6) < 1e-9
    assert abs(result.instructions[1].params[0] - 0.6) < 1e-9