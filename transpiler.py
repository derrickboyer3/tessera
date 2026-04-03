from qiskit import QuantumCircuit

class TesseraTranspiler:
    def __init__(self, qc, hardware_layout):
        self.qc = qc
        self.hw = hardware_layout

    def get_info(self):
        return f"Tessera Transpiler Statistics & Info:\n\tQuantum Circuitry (before transpile):\n{self.qc}\n\tHardware Layout (qubit config): {self.hw}"
