from instruction import TesseraInstruction

def test_basic_creation():
    inst = TesseraInstruction("h", [0])
    assert inst.name == "h"
    assert inst.qubits == [0]
    assert inst.clbits == []
    assert inst.params == []

def test_with_params():
    inst = TesseraInstruction("rz", [0], [], [1.57])
    assert inst.params == [1.57]

def test_with_clbits():
    inst = TesseraInstruction("measure", [0], [0])
    assert inst.clbits == [0]