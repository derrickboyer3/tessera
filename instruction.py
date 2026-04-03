'''
    Tessera Instruction Class
    -------------------------
    This class holds the data for an instruction. This include the type of instruction, the list of qubits & classical
    bits, and any parameters if the gates have them. Each field is outlines below:
        |---------------------------------------------------------------------------------------------------------------------------------|
        | Field Name | Description                                                                                                        |
        |------------+--------------------------------------------------------------------------------------------------------------------|
        | name       | The type of gate the instruction represents (i.e. H, CX, M, etc.)                                                  |
        |------------+--------------------------------------------------------------------------------------------------------------------|
        | qubits     | The array of integers representing qubits (i.e. An array of [0, 1, 2] represents a gate that involves q0, q1, & q2)|
        |------------+--------------------------------------------------------------------------------------------------------------------|
        | clbits     | The array of integers representing classical bits. Works the same as qubits                                        |
        |------------+--------------------------------------------------------------------------------------------------------------------|
        | params     | Any params for the instruction such as rotation angle                                                              |
        |---------------------------------------------------------------------------------------------------------------------------------|
'''
from dataclasses import dataclass, field

@dataclass
class TesseraInstruction:
    name: str
    qubits: list[int]
    clbits: list[int] = field(default_factory=list)
    params: list[float] = field(default_factory=list)