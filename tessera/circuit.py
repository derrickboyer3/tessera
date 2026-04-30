'''
      Tessera Circuit Class
    -------------------------
    This class holds the data for a circuit including the number of qubits, the number of classical bits
    and the list of instructions for the circuit. Each field is described in more detail below:
        |-------------------------------------------------------------------------------------------|
        | Field Name  | Description                                                                 |
        |-------------+-----------------------------------------------------------------------------|
        | num_qubits  | The number of qubits in the circuit                                         |
        |-------------+-----------------------------------------------------------------------------|
        | num_clbits  | The number of classical bits in the circuit                                 |
        |-------------+-----------------------------------------------------------------------------|
        | instructions| The array of instructions in the circuit. See instructions.py for reference |
        |-------------------------------------------------------------------------------------------|
'''
from dataclasses import dataclass, field
from tessera.instruction import TesseraInstruction

@dataclass
class TesseraCircuit:
    num_qubits: int
    num_clbits: int = 0
    instructions: list[TesseraInstruction] = field(default_factory=list)
    layout: dict[int, int] = field(default_factory=dict)