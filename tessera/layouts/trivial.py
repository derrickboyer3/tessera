'''
    Trivial Layout Algorithm
    ------------------------
    The simplest possible layout. Maps each logical qubit directly to the
    physical qubit with the same index (logical i -> physical i).

    Makes no attempt to optimize for hardware topology — useful as a
    baseline for testing, and for circuits whose qubit interactions
    already match the device connectivity.

    Args:
        circuit:      The TesseraCircuit whose qubits need to be laid out
        coupling_map: The TesseraCouplingMap representing hardware connectivity

    Returns:
        dict[int, int] mapping logical qubit indices to physical qubit indices.

    Raises:
        ValueError: If the circuit has more qubits than the coupling map supports.
'''
from tessera.circuit import TesseraCircuit
from tessera.hardware.coupling_map import TesseraCouplingMap


def trivial_layout(circuit: TesseraCircuit, coupling_map: TesseraCouplingMap) -> dict[int, int]:
    if circuit.num_qubits > len(coupling_map):
        raise ValueError(f"[Tessera]: Circuit has too many qubits for coupling map:\n\tCircuit Qubits: {circuit.num_qubits}\n\tCoupling Map Length: {len(coupling_map)}")
    return {i: i for i in range(circuit.num_qubits)}