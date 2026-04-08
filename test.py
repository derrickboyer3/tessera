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
from transpiler import TesseraTranspiler
import numpy as np
pi = np.pi
import time

print('Imports done.')

'''
qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 2)
qc.h(1)
qc.measure([0, 1, 2], [0, 1, 2])
'''

qc = QuantumCircuit(4, 4)

# Single qubit no-param gates
qc.h(0)
qc.x(1)
qc.y(2)
qc.z(3)
qc.s(0)
qc.sdg(1)
qc.t(2)
qc.tdg(3)
qc.sx(0)

# Single qubit parameterized gates
qc.rx(np.pi / 3, 1)
qc.ry(np.pi / 4, 2)
qc.rz(np.pi / 6, 3)
qc.p(np.pi / 2, 0)

# Two qubit gates
qc.cx(0, 1)
qc.cz(1, 2)
qc.cy(2, 3)
qc.swap(0, 3)
qc.cp(np.pi / 4, 0, 1)

# Three qubit
qc.ccx(0, 1, 2)

# Measurements
qc.measure([0, 1, 2, 3], [0, 1, 2, 3])

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

backend = "IBM"
transpiler = TesseraTranspiler(qiskit_circuit, backend, debug_on=True)
start = time.perf_counter()
translated_circuit = transpiler.execute()
end = time.perf_counter()
elapsed = end - start
print(f"Successfully transpiled Qiskit Quantum Circuit for {backend} backend using Tessera Transpiler:\n{translated_circuit}\nTime: {elapsed}s")

# Dense Layout Pass sanity check
from hardware.coupling_map import TesseraCouplingMap
from passes.dense_layout_pass import DenseLayoutPass
from passes.trivial_pass import TrivialPass
from circuit import TesseraCircuit
from instruction import TesseraInstruction

# Circuit where q0 and q1 interact a lot, q0 and q2 interact a little
test_circuit = TesseraCircuit(3, 0, [
    TesseraInstruction("cx", [0, 2], [], []),
    TesseraInstruction("cx", [0, 2], [], []),
    TesseraInstruction("cx", [0, 2], [], []),
    TesseraInstruction("cx", [0, 1], [], []),
])

# Linear coupling map: 0->1->2->3->4
cm = TesseraCouplingMap(5, [(0,1), (1,2), (2,3), (3,4)])

trivial_result = TrivialPass(cm).run(test_circuit)
dense_result = DenseLayoutPass(cm).run(test_circuit)

print(f"Trivial Layout: {trivial_result.layout}")
print(f"Dense Layout:   {dense_result.layout}")