'''
    Trivial Layout Pass
    -------------------
    The simplest possible layout pass. Maps each logical qubit in the circuit
    directly to the corresponding physical qubit on the device with the same
    index (logical qubit 0 -> physical qubit 0, logical qubit 1 -> physical
    qubit 1, etc.).

    This pass makes no attempt to optimize the mapping for hardware topology.
    It is used as a baseline for testing and for circuits whose qubit interactions
    already match the hardware connectivity.

    Raises:
        ValueError: If the circuit has more qubits than the coupling map supports.
'''
from tessera.circuit import TesseraCircuit
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.transpiler_pass import TranspilerPass

class TrivialPass(TranspilerPass):
    def __init__(self, coupling_map: TesseraCouplingMap):
        self.coupling_map = coupling_map

    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        if circuit.num_qubits > len(self.coupling_map):
            raise ValueError(f"[Tessera]: Circuit has too many qubits for coupling map:\n\tCircuit Qubits: {circuit.num_qubits}\n\tCoupling Map Length: {len(self.coupling_map)}")
        num_qubits = circuit.num_qubits
        num_clbits = circuit.num_clbits
        instructions = circuit.instructions
        layout = {i: i for i in range(num_qubits)}
        return TesseraCircuit(num_qubits, num_clbits, instructions, layout)
