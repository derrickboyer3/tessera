'''
    Identity Pass
    -------------
    A trivial no-op transpiler pass that returns the circuit completely unchanged.
    Used to verify that the pass infrastructure and PassManager are wired up
    correctly. If a circuit round-trips through this pass and comes out identical,
    the pipeline is working as expected.
'''
from tessera.circuit import TesseraCircuit
from tessera.transpiler_pass import TranspilerPass

class IdentityPass(TranspilerPass):
    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        return circuit