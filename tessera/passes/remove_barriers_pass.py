'''
    Remove Barriers Pass
    --------------------
    Transpiler pass that strips all barrier instructions from a TesseraCircuit.
    Barriers are structural hints used during circuit construction to prevent
    reordering across a boundary, but they have no physical effect on hardware.
    Removing them before optimization allows passes like CancelAdjacentPass and
    MergeRotationsPass to see through them and find cancellation and merging
    opportunities they would otherwise miss.

    This pass should be run after routing and before optimization passes.
'''
from tessera.circuit import TesseraCircuit
from tessera.transpiler_pass import TranspilerPass

class RemoveBarriersPass(TranspilerPass):
    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        result = []
        for ins in circuit.instructions:
            if ins.name != "barrier":
                result.append(ins)

        return TesseraCircuit(circuit.num_qubits, circuit.num_clbits, result, circuit.layout)

