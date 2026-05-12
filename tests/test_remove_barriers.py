'''
    Tests for RemoveBarriersPass
    -----------------------------
    Covers barrier removal, pass-through of non-barrier instructions,
    edge cases, and preservation of circuit metadata.
'''
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.passes.remove_barriers_pass import RemoveBarriersPass

# ── Helpers ───────────────────────────────────────────────────────────────────

def make_circuit(*instructions):
    return TesseraCircuit(num_qubits=3, num_clbits=0, instructions=list(instructions))

def ins(name, qubits):
    return TesseraInstruction(name=name, qubits=qubits)

# ── Tests ─────────────────────────────────────────────────────────────────────

def test_removes_single_barrier():
    circ = make_circuit(ins("barrier", [0, 1, 2]))
    result = RemoveBarriersPass().run(circ)
    assert result.instructions == []

def test_removes_multiple_barriers():
    circ = make_circuit(ins("barrier", [0]), ins("barrier", [1]), ins("barrier", [2]))
    result = RemoveBarriersPass().run(circ)
    assert result.instructions == []

def test_preserves_non_barrier_gates():
    circ = make_circuit(ins("x", [0]), ins("cx", [0, 1]))
    result = RemoveBarriersPass().run(circ)
    assert len(result.instructions) == 2

def test_removes_barrier_between_gates():
    circ = make_circuit(ins("h", [0]), ins("barrier", [0, 1, 2]), ins("h", [0]))
    result = RemoveBarriersPass().run(circ)
    assert len(result.instructions) == 2
    assert all(i.name != "barrier" for i in result.instructions)

def test_empty_circuit():
    circ = make_circuit()
    result = RemoveBarriersPass().run(circ)
    assert result.instructions == []

def test_no_barriers_unchanged():
    circ = make_circuit(ins("x", [0]), ins("h", [1]), ins("cx", [0, 1]))
    result = RemoveBarriersPass().run(circ)
    assert len(result.instructions) == 3

def test_preserves_layout_and_clbits():
    circ = TesseraCircuit(num_qubits=2, num_clbits=2, instructions=[ins("barrier", [0, 1])], layout={0: 1, 1: 2})
    result = RemoveBarriersPass().run(circ)
    assert result.instructions == []
    assert result.layout == {0: 1, 1: 2}
    assert result.num_clbits == 2

def test_preserves_instruction_order():
    circ = make_circuit(ins("h", [0]), ins("barrier", [0, 1]), ins("x", [1]), ins("barrier", [0, 1]), ins("cx", [0, 1]))
    result = RemoveBarriersPass().run(circ)
    assert len(result.instructions) == 3
    assert [i.name for i in result.instructions] == ["h", "x", "cx"]