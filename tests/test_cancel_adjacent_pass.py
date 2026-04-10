'''
    Tests for CancelAdjacentPass
    -----------------------------
    Covers strict and commutative modes for self-inverse gate cancellation.
    Tests happy path, edge cases, and mixed circuit scenarios.
'''
import pytest
from circuit import TesseraCircuit
from instruction import TesseraInstruction
from passes.cancel_adjacent_pass import CancelAdjacentPass

# ── Helpers ──────────────────────────────────────────────────────────────────

def make_circuit(*instructions):
    return TesseraCircuit(num_qubits=3, num_clbits=0, instructions=list(instructions))

def ins(name, qubits, params=None):
    return TesseraInstruction(name=name, qubits=qubits, params=params or [])

# ── Strict Mode ───────────────────────────────────────────────────────────────

def test_strict_cancels_adjacent_x():
    circ = make_circuit(ins("x", [0]), ins("x", [0]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert result.instructions == []

def test_strict_cancels_adjacent_cx():
    circ = make_circuit(ins("cx", [0, 1]), ins("cx", [0, 1]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert result.instructions == []

def test_strict_cancels_adjacent_h():
    circ = make_circuit(ins("h", [0]), ins("h", [0]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert result.instructions == []

def test_strict_no_cancel_different_qubits():
    circ = make_circuit(ins("x", [0]), ins("x", [1]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert len(result.instructions) == 2

def test_strict_no_cancel_non_adjacent():
    circ = make_circuit(ins("h", [0]), ins("x", [1]), ins("h", [0]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert len(result.instructions) == 3

def test_strict_no_cancel_different_gates():
    circ = make_circuit(ins("x", [0]), ins("h", [0]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert len(result.instructions) == 2

def test_strict_triple_x_leaves_one():
    circ = make_circuit(ins("x", [0]), ins("x", [0]), ins("x", [0]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert len(result.instructions) == 1
    assert result.instructions[0].name == "x"

def test_strict_quad_x_cancels_all():
    circ = make_circuit(ins("x", [0]), ins("x", [0]), ins("x", [0]), ins("x", [0]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert result.instructions == []

def test_strict_preserves_non_self_inverse():
    circ = make_circuit(ins("rz", [0], [0.5]), ins("rz", [0], [0.5]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert len(result.instructions) == 2

def test_strict_preserves_layout_and_clbits():
    circ = TesseraCircuit(num_qubits=2, num_clbits=2, instructions=[ins("x", [0]), ins("x", [0])], layout={0: 1, 1: 2})
    result = CancelAdjacentPass(strict=True).run(circ)
    assert result.instructions == []
    assert result.layout == {0: 1, 1: 2}
    assert result.num_clbits == 2

def test_strict_empty_circuit():
    circ = make_circuit()
    result = CancelAdjacentPass(strict=True).run(circ)
    assert result.instructions == []

def test_strict_single_gate_no_cancel():
    circ = make_circuit(ins("x", [0]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert len(result.instructions) == 1

def test_strict_cx_wrong_order_no_cancel():
    circ = make_circuit(ins("cx", [0, 1]), ins("cx", [1, 0]))
    result = CancelAdjacentPass(strict=True).run(circ)
    assert len(result.instructions) == 2

# ── Commutative Mode ──────────────────────────────────────────────────────────

def test_commutative_cancels_adjacent():
    circ = make_circuit(ins("x", [0]), ins("x", [0]))
    result = CancelAdjacentPass(strict=False).run(circ)
    assert result.instructions == []

def test_commutative_cancels_across_non_overlapping():
    circ = make_circuit(ins("h", [0]), ins("x", [1]), ins("h", [0]))
    result = CancelAdjacentPass(strict=False).run(circ)
    assert len(result.instructions) == 1
    assert result.instructions[0].name == "x"

def test_commutative_blocked_by_overlapping_gate():
    circ = make_circuit(ins("h", [0]), ins("x", [0]), ins("h", [0]))
    result = CancelAdjacentPass(strict=False).run(circ)
    assert len(result.instructions) == 3

def test_commutative_no_cancel_different_qubits():
    circ = make_circuit(ins("x", [0]), ins("x", [1]))
    result = CancelAdjacentPass(strict=False).run(circ)
    assert len(result.instructions) == 2

def test_commutative_empty_circuit():
    circ = make_circuit()
    result = CancelAdjacentPass(strict=False).run(circ)
    assert result.instructions == []

def test_commutative_preserves_layout():
    circ = TesseraCircuit(num_qubits=2, num_clbits=0, instructions=[ins("h", [0]), ins("x", [1]), ins("h", [0])], layout={0: 2, 1: 3})
    result = CancelAdjacentPass(strict=False).run(circ)
    assert result.layout == {0: 2, 1: 3}