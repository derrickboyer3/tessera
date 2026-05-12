'''
    Our mapping library for converting the Tessera 'name' field from a TesseraInstruction
    back into an actual Qiskit Gate object when converting back and forth between the two
    storage formats. When necessary, import new ones and simply add their mapping to the
    GATE_MAP below
'''
from qiskit.circuit.library import (
    HGate, XGate, YGate, ZGate, SGate, SdgGate, TGate, TdgGate,
    SXGate, RXGate, RYGate, RZGate, PhaseGate, UGate, CXGate,
    CZGate, CYGate, SwapGate, CPhaseGate, CCXGate
)
from qiskit.circuit.measure import Measure

GATE_MAP = {
    # Single-qubit, no params
    "h":       lambda p: HGate(),
    "x":       lambda p: XGate(),
    "y":       lambda p: YGate(),
    "z":       lambda p: ZGate(),
    "s":       lambda p: SGate(),
    "sdg":     lambda p: SdgGate(),
    "t":       lambda p: TGate(),
    "tdg":     lambda p: TdgGate(),
    "sx":      lambda p: SXGate(),

    # Single-qubit, with params
    "rx":      lambda p: RXGate(p[0]),
    "ry":      lambda p: RYGate(p[0]),
    "rz":      lambda p: RZGate(p[0]),
    "p":       lambda p: PhaseGate(p[0]),
    "u":       lambda p: UGate(p[0], p[1], p[2]),

    # Two-qubit
    "cx":      lambda p: CXGate(),
    "cnot":    lambda p: CXGate(),
    "cz":      lambda p: CZGate(),
    "cy":      lambda p: CYGate(),
    "swap":    lambda p: SwapGate(),
    "cp":      lambda p: CPhaseGate(p[0]),

    # Three-qubit
    "ccx":     lambda p: CCXGate(),

    # Measurement
    "measure": lambda p: Measure(),
}