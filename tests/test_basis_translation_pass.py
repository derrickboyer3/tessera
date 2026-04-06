from circuit import TesseraCircuit
from instruction import TesseraInstruction
from passes.basis_translation_pass import BasisTranslationPass
from backends.basis_gate_sets import IBM_BASIS_GATES
import pytest
import numpy as np
pi = np.pi

def run_pass(instructions, num_qubits=2, num_clbits=0):
    circuit = TesseraCircuit(num_qubits, num_clbits, instructions)
    return BasisTranslationPass(backend="IBM").run(circuit)

def test_basis_gates_pass_through():
    result = run_pass([TesseraInstruction("cx", [0, 1], [], [])])
    assert result.instructions[0].name == "cx"

def test_h_decomposes():
    result = run_pass([TesseraInstruction("h", [0], [], [])])
    assert all(i.name in IBM_BASIS_GATES for i in result.instructions)
    assert len(result.instructions) == 3

def test_measure_passes_through():
    result = run_pass([TesseraInstruction("measure", [0], [0], [])], num_clbits=1)
    assert result.instructions[0].name == "measure"

def test_cnot_normalized_to_cx():
    result = run_pass([TesseraInstruction("cnot", [0, 1], [], [])])
    assert result.instructions[0].name == "cx"

def test_qubit_remapping():
    result = run_pass([TesseraInstruction("h", [1], [], [])], num_qubits=2)
    for ins in result.instructions:
        assert 1 in ins.qubits

def test_unknown_gate_raises():
    with pytest.raises(ValueError, match="No decomposition found"):
        run_pass([TesseraInstruction("fakegate", [0], [], [])])

def test_all_output_gates_are_basis():
    instructions = [
        TesseraInstruction("h", [0], [], []),
        TesseraInstruction("y", [1], [], []),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("swap", [0, 1], [], []),
    ]
    result = run_pass(instructions)
    for ins in result.instructions:
        assert ins.name in IBM_BASIS_GATES

def test_unknown_backend():
    instructions = [
        TesseraInstruction("h", [0], [], []),
        TesseraInstruction("y", [1], [], []),
        TesseraInstruction("cz", [0, 1], [], []),
        TesseraInstruction("swap", [0, 1], [], []),
    ]
    circuit = TesseraCircuit(2, 0, instructions)
    circ = BasisTranslationPass(backend="UNKNOWN").run(circuit)
    assert circ == circuit