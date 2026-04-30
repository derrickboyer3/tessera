from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.passes.identity_pass import IdentityPass

def test_identity_returns_same_circuit():
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("h", [0]),
        TesseraInstruction("cx", [0, 1])
    ])
    result = IdentityPass().run(circuit)
    assert result == circuit

def test_identity_does_not_modify_instructions():
    circuit = TesseraCircuit(2, 0, [TesseraInstruction("h", [0])])
    result = IdentityPass().run(circuit)
    assert len(result.instructions) == 1
    assert result.instructions[0].name == "h"