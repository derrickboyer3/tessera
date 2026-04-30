from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.pass_manager import TesseraPassManager
from tessera.transpiler_pass import TranspilerPass

def make_test_circuit():
    return TesseraCircuit(2, 0, [
        TesseraInstruction("h", [0]),
        TesseraInstruction("cx", [0, 1])
    ])

def test_empty_pipeline():
    manager = TesseraPassManager()
    circuit = make_test_circuit()
    result = manager.run(circuit)
    assert result == circuit

def test_add_pass():
    manager = TesseraPassManager()
    assert len(manager.passes) == 0

    class DummyPass(TranspilerPass):
        def run(self, circuit): return circuit

    manager.add_pass(DummyPass())
    assert len(manager.passes) == 1

def test_clear():
    class DummyPass(TranspilerPass):
        def run(self, circuit): return circuit

    manager = TesseraPassManager([DummyPass()])
    manager.clear()
    assert manager.passes == []

def test_before_after_hooks():
    log = []

    class DummyPass(TranspilerPass):
        def run(self, circuit): return circuit

    manager = TesseraPassManager([DummyPass()])
    manager.run(
        make_test_circuit(),
        before=lambda p, c: log.append(f"before:{p.name}"),
        after=lambda p, c: log.append(f"after:{p.name}")
    )
    assert log == ["before:DummyPass", "after:DummyPass"]