'''
    Tessera Layout Registry
    -----------------------
    Central registry mapping layout algorithm names to their implementations.
    When adding a new layout algorithm, create a new file under tessera/layouts/,
    implement the algorithm as a function matching the signature below, then
    add an entry here. No other files need to change.

    Each registered algorithm is a callable matching the signature:

        layout_fn(circuit: TesseraCircuit, coupling_map: TesseraCouplingMap) -> dict[int, int]

    where the returned dict maps logical qubit indices to physical qubit indices.

    Available algorithms:
        - trivial: direct mapping of logical to physical qubits (see trivial.py)
        - dense: greedy interaction-frequency placement (see dense.py)
        - sabre: advanced heuristic placement (see sabre.py)
'''
from tessera.layouts.trivial import trivial_layout
from tessera.layouts.dense import dense_layout
from tessera.layouts.sabre import sabre_layout

LAYOUT_REGISTRY = {
    "trivial": trivial_layout,
    "dense": dense_layout,
    "sabre": sabre_layout
}