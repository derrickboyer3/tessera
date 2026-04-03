from qiskit import QuantumCircuit
from converters import from_qiskit, to_qiskit

print('Imports done.')

qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 2)
qc.h(1)
qc.measure([0, 1, 2], [0, 1, 2])

tessera_circuit = from_qiskit(qc)
print(f"Successfully converted Qiskit Quantum Circuit to Tessera Quantum Circuit: {tessera_circuit}")

qiskit_circuit = to_qiskit(tessera_circuit)
print(f"Successfully converted Tessera Quantum Circuit to Qiskit Quantum Circuit:\n{qiskit_circuit}")