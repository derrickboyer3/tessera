'''
    Tests for OptimizationLoopPass
    ------------------------------
    Covers fixed-iteration mode, convergence mode, validation, max_iterations
    safety cap, debug logging, and layout/clbit preservation.
'''
import pytest
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.transpiler_pass import TranspilerPass
from tessera.passes.optimization_loop_pass import OptimizationLoopPass

# Helpers

def make_circuit(*instructions, num_qubits=2, num_clbits=0, layout=None):
    return TesseraCircuit(
        num_qubits=num_qubits,
        num_clbits=num_clbits,
        instructions=list(instructions),
        layout=layout or {},
    )

def ins(name, qubits, params=None):
    return TesseraInstruction(name=name, qubits=qubits, params=params or [])

# A pass that records how many times it ran. Identity behavior on the circuit.
class CountingPass(TranspilerPass):
    def __init__(self):
        self.calls = 0

    def run(self, circuit):
        self.calls += 1
        return circuit

# A pass that drops the first instruction each call until the circuit is empty.
# Useful for exercising convergence — gate count strictly decreases, then stalls.
class ShrinkingPass(TranspilerPass):
    def __init__(self):
        self.calls = 0

    def run(self, circuit):
        self.calls += 1
        new_ins = circuit.instructions[1:] if circuit.instructions else []
        return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, new_ins, circuit.layout)



# Validation

def test_invalid_iterations_zero():
    with pytest.raises(ValueError):
        OptimizationLoopPass([], optimization_iterations=0)

def test_invalid_iterations_negative_two():
    with pytest.raises(ValueError):
        OptimizationLoopPass([], optimization_iterations=-2)

def test_invalid_max_iterations_zero():
    with pytest.raises(ValueError):
        OptimizationLoopPass([], optimization_iterations=-1, max_iterations=0)

def test_invalid_max_iterations_negative():
    with pytest.raises(ValueError):
        OptimizationLoopPass([], optimization_iterations=-1, max_iterations=-5)

def test_valid_iterations_default():
    OptimizationLoopPass([], optimization_iterations=1)

def test_valid_iterations_convergence():
    OptimizationLoopPass([], optimization_iterations=-1)


# Fixed-Iteration Mode

def test_default_iterations_runs_once():
    p = CountingPass()
    loop = OptimizationLoopPass([p])
    loop.run(make_circuit(ins("x", [0])))
    assert p.calls == 1

def test_fixed_iterations_runs_exact_count():
    p = CountingPass()
    loop = OptimizationLoopPass([p], optimization_iterations=5)
    loop.run(make_circuit(ins("x", [0])))
    assert p.calls == 5

def test_fixed_iterations_runs_all_inner_passes_each_loop():
    p1, p2 = CountingPass(), CountingPass()
    loop = OptimizationLoopPass([p1, p2], optimization_iterations=3)
    loop.run(make_circuit(ins("x", [0])))
    assert p1.calls == 3
    assert p2.calls == 3

def test_fixed_iterations_with_empty_pass_list_is_noop():
    circ = make_circuit(ins("x", [0]), ins("h", [1]))
    result = OptimizationLoopPass([], optimization_iterations=4).run(circ)
    assert result.instructions == circ.instructions

def test_fixed_iterations_preserves_layout_and_clbits():
    circ = make_circuit(ins("x", [0]), num_clbits=2, layout={0: 3, 1: 4})
    result = OptimizationLoopPass([CountingPass()]).run(circ)
    assert result.layout == {0: 3, 1: 4}
    assert result.num_clbits == 2


# Convergence Mode

def test_convergence_stops_when_no_improvement():
    p = CountingPass()
    loop = OptimizationLoopPass([p], optimization_iterations=-1)
    loop.run(make_circuit(ins("x", [0])))
    # CountingPass never changes gate count — should run exactly twice:
    # once to establish a baseline, once to detect no improvement.
    assert p.calls == 2

def test_convergence_runs_until_shrinking_stalls():
    p = ShrinkingPass()
    circ = make_circuit(ins("x", [0]), ins("x", [0]), ins("x", [0]))
    result = OptimizationLoopPass([p], optimization_iterations=-1).run(circ)
    # Each call drops one instruction until empty, then one more confirms stall.
    assert result.instructions == []
    assert p.calls == 4

def test_convergence_honors_max_iterations_cap(capsys):
    p = ShrinkingPass()
    # 10 instructions, cap at 3: ShrinkingPass strictly reduces gate count each
    # iteration, so the no-improvement break never fires before the cap does.
    big_circ = make_circuit(*[ins("x", [0]) for _ in range(10)])
    loop = OptimizationLoopPass(
        [p], optimization_iterations=-1, max_iterations=3, debug_on=True
    )
    loop.run(big_circ)
    assert p.calls == 3
    captured = capsys.readouterr()
    assert "Reached maximum iterations" in captured.out

def test_convergence_preserves_layout():
    circ = make_circuit(ins("x", [0]), num_clbits=1, layout={0: 7})
    result = OptimizationLoopPass([CountingPass()], optimization_iterations=-1).run(circ)
    assert result.layout == {0: 7}
    assert result.num_clbits == 1


# Debug Logging

def test_debug_on_prints_before_and_after_each_pass(capsys):
    p = CountingPass()
    loop = OptimizationLoopPass([p], optimization_iterations=2, debug_on=True)
    loop.run(make_circuit(ins("x", [0])))
    captured = capsys.readouterr()
    assert captured.out.count("Running pass: CountingPass") == 2
    assert captured.out.count("Finished pass: CountingPass") == 2

def test_debug_off_is_silent(capsys):
    p = CountingPass()
    loop = OptimizationLoopPass([p], optimization_iterations=2, debug_on=False)
    loop.run(make_circuit(ins("x", [0])))
    captured = capsys.readouterr()
    assert captured.out == ""

def test_debug_on_in_convergence_mode_prints(capsys):
    p = CountingPass()
    loop = OptimizationLoopPass([p], optimization_iterations=-1, debug_on=True)
    loop.run(make_circuit(ins("x", [0])))
    captured = capsys.readouterr()
    assert "Running pass: CountingPass" in captured.out
    assert "Finished pass: CountingPass" in captured.out
