'''
    Catch all test file. This file is a script that runs through all functions and libraries to ensure correct output
    from traditional usage. Update and add on as new features are added to the Tessera Quantum Transpiler. This is not
    a full, proper PyTest style file, this is more of a traditional usage test file to verify correct outputs from 
    traditional implementations using our transpiler
'''
from qiskit import QuantumCircuit
from converters import from_qiskit, to_qiskit
from pass_manager import TesseraPassManager
from passes.identity_pass import IdentityPass

print('Imports done.')

qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 2)
qc.h(1)
qc.measure([0, 1, 2], [0, 1, 2])

tessera_circuit = from_qiskit(qc)
print(f"Successfully converted Qiskit Quantum Circuit to Tessera Quantum Circuit: {tessera_circuit}")

def log_before(pass_, circuit):
    print(f"[Tessera] Running pass: {pass_.name} | Gates: {len(circuit.instructions)}")

def log_after(pass_, circuit):
    print(f"[Tessera] Finished pass: {pass_.name} | Gates: {len(circuit.instructions)}")
manager = TesseraPassManager([IdentityPass()])
result = manager.run(tessera_circuit, before=log_before, after=log_after)

qiskit_circuit = to_qiskit(tessera_circuit)
print(f"Successfully converted Tessera Quantum Circuit to Qiskit Quantum Circuit:\n{qiskit_circuit}")