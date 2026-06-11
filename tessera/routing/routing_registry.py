'''
    Tessera Routing Registry
    ------------------------
    Central registry mapping routing algorithm names to whole-circuit
    routing strategies. When adding a new routing algorithm, create a new
    file under tessera/routing/, implement the algorithm matching the
    contract below, then add an entry here. No other files need to change.

    Each registered strategy is a callable matching the signature:

        strategy(circuit: TesseraCircuit, coupling_map: TesseraCouplingMap) -> TesseraCircuit

    that takes a layout-mapped circuit and returns a routed circuit with
    SWAPs inserted as needed.

    Pairwise algorithms (BFS, A*) share the pairwise_route engine — their
    registry entries are thin wrappers that call pairwise_route with the
    appropriate path-finder. SABRE is registered directly because its
    whole-circuit swap selection does not fit the pairwise contract.

    Available algorithms:
        - bfs:    breadth-first pathfinding (see bfs.py + pairwise.py)
        - a_star: A* pathfinding with hop-distance heuristic (see a_star.py + pairwise.py)
        - sabre:  whole-circuit heuristic swap selection (see sabre.py)
'''
from tessera.routing.bfs import bfs_path
from tessera.routing.a_star import a_star_path
from tessera.routing.sabre import sabre_route
from tessera.routing.pairwise import pairwise_route

def bfs_strategy(circuit, coupling_map):
    return pairwise_route(circuit, coupling_map, lambda s, e: bfs_path(coupling_map, s, e))

def a_star_strategy(circuit, coupling_map):
    return pairwise_route(circuit, coupling_map, lambda s, e: a_star_path(coupling_map, s, e))

ROUTING_REGISTRY = {
    "bfs": bfs_strategy,
    "a_star": a_star_strategy,
    "sabre": sabre_route
}