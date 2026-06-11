'''
    Basic Swap Router
    -----------------
    A transpiler pass that routes a layout-mapped circuit to be compatible with the
    physical connectivity constraints of the target hardware. Delegates the actual
    routing work to a strategy selected at construction time — the pass itself is
    a thin shell that resolves the algorithm choice and calls into it.

    The routing strategy is pluggable. Pass either a registered algorithm name
    (string) or a custom callable that matches the pairwise path-finder signature:

        path_finder(start: int, end: int) -> list[int]

    where the returned list is a path of physical qubits from start to end.

    String names are resolved through ROUTING_REGISTRY at construction time, so
    unknown names fail immediately rather than at run time. Custom callables are
    wrapped internally with pairwise_route to produce a whole-circuit strategy.

    Args:
        coupling_map: The TesseraCouplingMap representing hardware connectivity.
        path_finder:  A registered algorithm name (e.g. "bfs", "a_star", "sabre")
                      or a custom pairwise pathfinder callable. Defaults to "bfs".
                      None is treated as "bfs" for backwards compatibility.

    Available algorithms (from ROUTING_REGISTRY):
        - "bfs":    breadth-first pathfinding (default)
        - "a_star": A* pathfinding with hop-distance heuristic
        - "sabre":  whole-circuit heuristic swap selection with front-layer lookahead

    Raises:
        ValueError: If path_finder is a string that is not registered in ROUTING_REGISTRY.
        ValueError: If path_finder is neither a string nor a callable.
        ValueError (at run time): If the input circuit has no layout.
        ValueError (at run time): If a gate with more than 2 qubits is encountered.
'''
from tessera.circuit import TesseraCircuit
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.transpiler_pass import TranspilerPass
from tessera.instruction import TesseraInstruction
from tessera.routing.pairwise import pairwise_route
from tessera.routing.routing_registry import ROUTING_REGISTRY

class BasicSwapRouter(TranspilerPass):
    def __init__(self, coupling_map: TesseraCouplingMap, path_finder="bfs"):
        self.coupling_map = coupling_map
        if path_finder is None:
            path_finder = "bfs"
        if isinstance(path_finder, str):
            if path_finder not in ROUTING_REGISTRY:
                raise ValueError(f"[Tessera]: Unknown routing strategy '{path_finder}'. Available strategies: {list(ROUTING_REGISTRY.keys())}")
            self.strategy_fn = ROUTING_REGISTRY[path_finder]
        elif callable(path_finder):
            self.strategy_fn = lambda circuit, coupling_map: pairwise_route(circuit, coupling_map, path_finder)
        else:
            raise ValueError(f"[Tessera]: path_finder must be a string or callable, got {type(path_finder)}")

    def run(self, circuit: TesseraCircuit) -> TesseraCircuit:
        return self.strategy_fn(circuit, self.coupling_map)