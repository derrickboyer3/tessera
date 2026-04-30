from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction

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

def test_with_layout():
    layout = {0: 0, 1: 1, 2: 2}
    tc = TesseraCircuit(3, 0, [], layout)
    assert tc.layout == {0: 0, 1: 1, 2: 2}

def test_default_layout_is_empty():
    tc = TesseraCircuit(2)
    assert tc.layout == {}