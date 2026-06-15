'''
    SABRE Layout Algorithm
    ----------------------
    Initial-mapping discovery using forward-backward trial routing, based on
    Li, Ding, Xie (2019), "Tackling the Qubit Mapping Problem for NISQ-Era
    Quantum Devices."

    The quality of a routing pass depends heavily on the initial qubit
    mapping, but choosing a good mapping requires knowing how the circuit
    will route. SABRE layout breaks this chicken-and-egg by using the
    routing pass itself as a discovery tool: each trial routing pass's
    local swap decisions reveal which qubits would have benefited from
    starting closer together, and the END mapping of one pass becomes the
    START mapping of the next.

    Algorithm:
        1. Start with a trivial mapping (logical i -> physical i).
        2. FORWARD pass: trial-route the circuit with the trivial mapping.
           Record the mapping that results from the router's swap decisions.
        3. BACKWARD pass: trial-route the REVERSED circuit using the forward
           pass's end mapping as its starting mapping. Record the new end
           mapping.
        4. Return the backward pass's end mapping as the discovered initial
           layout. (This is the START mapping that the paper's final forward
           pass would have used — running that final pass is unnecessary for
           layout discovery since it produces no additional mapping info.)

    Uses the SABRE routing algorithm internally as the trial router. The
    final mapping after a trial pass is recovered by replaying the emitted
    swap instructions onto a copy of the initial mapping — no internals of
    the routing implementation are exposed.

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
from tessera.routing.sabre import sabre_route


def _trial_route_final_mapping(circuit, coupling_map, initial_mapping):
    # Run a trial SABRE route from the given initial mapping and recover the
    # final mapping by replaying emitted swaps onto a copy of it.
    trial_circ = TesseraCircuit(
        circuit.num_qubits,
        circuit.num_clbits,
        circuit.instructions,
        dict(initial_mapping),
    )
    routed = sabre_route(trial_circ, coupling_map)

    mapping = dict(initial_mapping)
    inverse = {v: k for k, v in mapping.items()}
    for ins in routed.instructions:
        if ins.name == "swap":
            p0, p1 = ins.qubits[0], ins.qubits[1]
            log0 = inverse.get(p0)
            log1 = inverse.get(p1)
            if log0 is not None:
                mapping[log0] = p1
            if log1 is not None:
                mapping[log1] = p0
            if log0 is not None and log1 is not None:
                inverse[p0], inverse[p1] = log1, log0
            elif log0 is not None:
                inverse[p1] = log0
                del inverse[p0]
            elif log1 is not None:  # pragma: no cover
                # Replays swaps emitted by sabre_route, which itself only produces
                # (mapped, unmapped) or (mapped, mapped) swaps in practice. Kept
                # for symmetry with the elif log0 branch.
                inverse[p0] = log1
                del inverse[p1]
    return mapping


def sabre_layout(circuit: TesseraCircuit, coupling_map: TesseraCouplingMap) -> dict[int, int]:
    if circuit.num_qubits > len(coupling_map):
        raise ValueError(f"[Tessera]: Circuit has too many qubits for coupling map:\n\tCircuit Qubits: {circuit.num_qubits}\n\tCoupling Map Length: {len(coupling_map)}")

    # Step 1: trivial starting mapping.
    mapping = {q: q for q in range(circuit.num_qubits)}

    # Step 2: forward pass on the original circuit.
    mapping = _trial_route_final_mapping(circuit, coupling_map, mapping)

    # Step 3: backward pass on the reversed circuit, starting from the
    # forward pass's end mapping.
    reversed_circ = TesseraCircuit(
        circuit.num_qubits,
        circuit.num_clbits,
        list(reversed(circuit.instructions)),
        {},  # layout is overridden by _trial_route_final_mapping
    )
    mapping = _trial_route_final_mapping(reversed_circ, coupling_map, mapping)

    return mapping
