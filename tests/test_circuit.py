from circuit import TesseraCircuit
from instruction import TesseraInstruction

def test_basic_creation():
    tc = TesseraCircuit(2)
    assert tc.num_qubits == 2
    assert tc.num_clbits == 0
    assert tc.instructions == []

def test_with_instructions():
    inst = TesseraInstruction("h", [0])
    tc = TesseraCircuit(1, 0, [inst])
    assert len(tc.instructions) == 1
    assert tc.instructions[0].name == "h"