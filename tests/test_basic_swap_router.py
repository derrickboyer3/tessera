from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.passes.basic_swap_router import BasicSwapRouter
import pytest

def make_linear_map():
    # 0->1->2->3
    return TesseraCouplingMap(4, [(0,1), (1,2), (2,3)])

def make_circuit(instructions, layout, num_qubits=4, num_clbits=0):
    return TesseraCircuit(num_qubits, num_clbits, instructions, layout)

# --- Layout Application Tests ---

def test_layout_applied_to_single_qubit_gate():
    circuit = make_circuit(
        [TesseraInstruction("x", [0], [], [])],
        layout={0: 2}
    )
    result = BasicSwapRouter(make_linear_map()).run(circuit)
    assert result.instructions[0].qubits == [2]

def test_layout_applied_to_two_qubit_gate():
    circuit = make_circuit(
        [TesseraInstruction("cx", [0, 1], [], [])],
        layout={0: 0, 1: 1}
    )
    result = BasicSwapRouter(make_linear_map()).run(circuit)
    assert result.instructions[0].qubits == [0, 1]

def test_no_layout_raises():
    circuit = TesseraCircuit(2, 0, [
        TesseraInstruction("cx", [0, 1], [], [])
    ])
    with pytest.raises(ValueError, match="No layout found"):
        BasicSwapRouter(make_linear_map()).run(circuit)

# --- Passthrough Tests ---

def test_single_qubit_gate_passes_through():
    circuit = make_circuit(
        [TesseraInstruction("x", [0], [], [])],
        layout={0: 0}
    )
    result = BasicSwapRouter(make_linear_map()).run(circuit)
    assert result.instructions[0].name == "x"

def test_measure_passes_through():
    circuit = make_circuit(
        [TesseraInstruction("measure", [0], [0], [])],
        layout={0: 0},
        num_clbits=1
    )
    result = BasicSwapRouter(make_linear_map()).run(circuit)
    assert result.instructions[0].name == "measure"

def test_adjacent_gate_no_swap_inserted():
    circuit = make_circuit(
        [TesseraInstruction("cx", [0, 1], [], [])],
        layout={0: 0, 1: 1}
    )
    result = BasicSwapRouter(make_linear_map()).run(circuit)
    assert len(result.instructions) == 1
    assert result.instructions[0].name == "cx"

# --- Swap Insertion Tests ---

def test_swap_inserted_for_non_adjacent_qubits():
    circuit = make_circuit(
        [TesseraInstruction("cx", [0, 2], [], [])],
        layout={0: 0, 1: 1, 2: 2}
    )
    result = BasicSwapRouter(make_linear_map()).run(circuit)
    names = [ins.name for ins in result.instructions]
    assert "swap" in names

def test_correct_gates_after_swap():
    circuit = make_circuit(
        [TesseraInstruction("cx", [0, 2], [], [])],
        layout={0: 0, 1: 1, 2: 2}
    )
    result = BasicSwapRouter(make_linear_map()).run(circuit)
    assert result.instructions[0].name == "swap"
    assert result.instructions[0].qubits == [0, 1]
    assert result.instructions[1].name == "cx"
    assert result.instructions[1].qubits == [1, 2]

def test_multiple_swaps_for_long_path():
    circuit = make_circuit(
        [TesseraInstruction("cx", [0, 3], [], [])],
        layout={0: 0, 1: 1, 2: 2, 3: 3}
    )
    result = BasicSwapRouter(make_linear_map()).run(circuit)
    names = [ins.name for ins in result.instructions]
    assert names.count("swap") == 2

def test_gate_count_increases_with_swaps():
    circuit = make_circuit(
        [TesseraInstruction("cx", [0, 2], [], [])],
        layout={0: 0, 1: 1, 2: 2}
    )
    result = BasicSwapRouter(make_linear_map()).run(circuit)
    assert len(result.instructions) > 1

# --- Error Handling Tests ---

def test_three_qubit_gate_raises():
    circuit = make_circuit(
        [TesseraInstruction("ccx", [0, 1, 2], [], [])],
        layout={0: 0, 1: 1, 2: 2}
    )
    with pytest.raises(ValueError, match="Decompose to 2-qubit gates"):
        BasicSwapRouter(make_linear_map()).run(circuit)

# --- Path Finder Resolution Tests ---

def test_default_path_finder_is_bfs():
    # Default should resolve through ROUTING_REGISTRY to bfs_strategy
    cm = TesseraCouplingMap(4, [(0,1), (1,2), (2,3)])
    circuit = make_circuit(
        [TesseraInstruction("cx", [0, 2], [], [])],
        layout={0: 0, 1: 1, 2: 2}
    )
    result = BasicSwapRouter(cm).run(circuit)
    names = [ins.name for ins in result.instructions]
    assert "swap" in names

def test_string_path_finder_a_star():
    cm = TesseraCouplingMap(4, [(0,1), (1,0), (1,2), (2,1), (2,3), (3,2)])
    circuit = make_circuit(
        [TesseraInstruction("cx", [0, 2], [], [])],
        layout={0: 0, 1: 1, 2: 2}
    )
    result = BasicSwapRouter(cm, path_finder="a_star").run(circuit)
    names = [ins.name for ins in result.instructions]
    assert "swap" in names

def test_string_path_finder_sabre():
    cm = TesseraCouplingMap(4, [(0,1), (1,0), (1,2), (2,1), (2,3), (3,2)])
    circuit = make_circuit(
        [TesseraInstruction("cx", [0, 2], [], [])],
        layout={0: 0, 1: 1, 2: 2}
    )
    result = BasicSwapRouter(cm, path_finder="sabre").run(circuit)
    names = [ins.name for ins in result.instructions]
    assert "swap" in names

def test_unknown_string_path_finder_raises():
    cm = TesseraCouplingMap(4, [(0,1), (1,2), (2,3)])
    with pytest.raises(ValueError, match="Unknown routing strategy"):
        BasicSwapRouter(cm, path_finder="not_a_real_algorithm")

def test_non_string_non_callable_path_finder_raises():
    cm = TesseraCouplingMap(4, [(0,1), (1,2), (2,3)])
    with pytest.raises(ValueError, match="must be a string or callable"):
        BasicSwapRouter(cm, path_finder=123)

def test_custom_callable_path_finder_called_for_non_adjacent():
    calls = []
    def custom_finder(start, end):
        calls.append((start, end))
        return [start, start+1, end]

    cm = TesseraCouplingMap(4, [(0,1), (1,2), (2,3)])
    circuit = make_circuit(
        [TesseraInstruction("cx", [0, 2], [], [])],
        layout={0: 0, 1: 1, 2: 2}
    )
    BasicSwapRouter(cm, path_finder=custom_finder).run(circuit)
    assert (0, 2) in calls