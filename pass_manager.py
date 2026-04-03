'''
    Tessera Pass Manager
    --------------------
    Manages and executes a sequential pipeline of TranspilerPass instances.
    Passes are run in order, with each pass receiving the output of the previous one.

    Usage:
        manager = TesseraPassManager([PassA(), PassB(), PassC()])
        result = manager.run(circuit)

    Passes can also be added incrementally via add_pass(). The pipeline can be
    cleared and rebuilt at any time using clear().
'''
from circuit import TesseraCircuit
from transpiler_pass import TranspilerPass

class TesseraPassManager:

    def __init__(self, passes: list[TranspilerPass] = None):
        self.passes = passes if passes is not None else []

    # Run passes sequentially with optional before/after hooks for debugging.
    # before(pass, circuit) is called with the circuit BEFORE the pass runs.
    # after(pass, circuit) is called with the circuit AFTER the pass runs.
    def run(self, circuit: TesseraCircuit, before=None, after=None) -> TesseraCircuit:
        for p in self.passes:
            if before:
                before(p, circuit)
            circuit = p.run(circuit)
            if after:
                after(p, circuit)
        return circuit

    def add_pass(self, p: TranspilerPass):
        self.passes.append(p)

    def clear(self):
        self.passes = []