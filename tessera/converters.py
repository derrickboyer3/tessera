'''
    A helper utility library for converting back and forth between Qiskit's quantum circuit data storage format
    and our Tessera quantum circuit storage format.

    1.) from_qiskit(qc: QuantumCircuit) => takes in a Qiskit quantum circuit and returns the Tessera formatted circuit
    2.) to_qiskit(tc: TesseraCircuit) => takes in a Tessera quantum circuit and returns the Qiskit formatted circuit

    Helpers:
    1.) gate_from_name(name: str, params: list) => Qiskit Gate Object
'''
from qiskit import QuantumCircuit
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.gate_library import GATE_MAP

# Helper function for creating a Qiskit Gate object from the Tessera 'name' field using out mapping library
def gate_from_name(name: str, params: list):
    if name not in GATE_MAP:
        raise ValueError(f"Tessera: Unknown gate '{name}' - if needed, add it to the GATE_MAP in gate_library.py")
    return GATE_MAP[name](params)

# Takes a Qiskit Quantum Circuit and parse the data to convert it into the Tessera format for a Quantum Circuit
def from_qiskit(qc: QuantumCircuit) -> TesseraCircuit:
    # Var initialization
    num_qubits = qc.num_qubits
    num_clbits = qc.num_clbits
    instructions = []

    # Loop through each instruction to fill out vars
    for ins in qc.data:
        # Operation name and params for ins
        op = ins.operation
        name = op.name
        params = [float(p) for p in op.params]

        # Create array of all involved qubits
        qbits = [qc.find_bit(q).index for q in ins.qubits]

        # Create an array of all involved classical bits
        clbits = [qc.find_bit(c).index for c in ins.clbits]

        # Creating the Tessera instruction and appending it to our circuit's array
        tessera_instruction = TesseraInstruction(name, qbits, clbits, params)
        instructions.append(tessera_instruction)

    # Create the full Tessera Circuit and return
    tessera_circuit = TesseraCircuit(num_qubits, num_clbits, instructions)
    return tessera_circuit

def to_qiskit(tc: TesseraCircuit):
    physical_qubits = max(tc.layout.values()) + 1 if tc.layout else tc.num_qubits
    qc = QuantumCircuit(physical_qubits, tc.num_clbits)

    for ins in tc.instructions:
        if ins.name == "barrier":
            qc.barrier(ins.qubits)
            continue
        gate = gate_from_name(ins.name, ins.params)
        qc.append(gate, ins.qubits, ins.clbits)

    return qc