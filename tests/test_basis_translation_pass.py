from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.passes.basis_translation_pass import BasisTranslationPass
from tessera.backends.basis_gate_sets import IBM_BASIS_GATES, IONQ_BASIS_GATES, RIGETTI_BASIS_GATES
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

def test_unknown_backend_raises():
    with pytest.raises(ValueError, match="Unknown backend"):
        BasisTranslationPass(backend="UNKNOWN")

def run_ionq_pass(instructions, num_qubits=2):
    return BasisTranslationPass(backend="IONQ").run(TesseraCircuit(num_qubits, 0, instructions))

def run_rigetti_pass(instructions, num_qubits=2):
    return BasisTranslationPass(backend="RIGETTI").run(TesseraCircuit(num_qubits, 0, instructions))

def test_ionq_h_decomposes_to_basis():
    result = run_ionq_pass([TesseraInstruction("h", [0], [], [])])
    assert all(i.name in IONQ_BASIS_GATES for i in result.instructions)

def test_ionq_x_decomposes_to_rx():
    result = run_ionq_pass([TesseraInstruction("x", [0], [], [])])
    assert result.instructions[0].name == "rx"

def test_ionq_output_contains_no_sx():
    result = run_ionq_pass([TesseraInstruction("sx", [0], [], [])])
    assert all(i.name != "sx" for i in result.instructions)

def test_rigetti_h_decomposes_to_basis():
    result = run_rigetti_pass([TesseraInstruction("h", [0], [], [])])
    assert all(i.name in RIGETTI_BASIS_GATES for i in result.instructions)

def test_rigetti_cx_decomposes_to_cz():
    result = run_rigetti_pass([TesseraInstruction("cx", [0, 1], [], [])])
    assert any(i.name == "cz" for i in result.instructions)
    assert all(i.name != "cx" for i in result.instructions)

def test_rigetti_full_output_only_basis():
    instructions = [
        TesseraInstruction("h", [0], [], []),
        TesseraInstruction("cx", [0, 1], [], []),
        TesseraInstruction("swap", [0, 1], [], []),
    ]
    result = run_rigetti_pass(instructions)
    assert all(i.name in RIGETTI_BASIS_GATES for i in result.instructions)