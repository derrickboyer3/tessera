'''
    A* Pathfinding
    --------------
    A* search over the coupling map's directed graph. Returns the shortest
    hop path between two physical qubits as a list of nodes (inclusive on
    both ends), guided by a heuristic that estimates remaining distance to
    the goal.

    Heuristic:
        Uses coupling_map.distance(node, end) — the true graph hop distance.
        This is admissible by definition, so A* is guaranteed to return an
        optimal path. The trade-off: on an unweighted coupling graph (every
        edge costs 1) the heuristic is the same shortest-path computation
        A* is trying to perform, so A* does not beat BFS on speed today.
        The architecture is correct and ready for future weighted-edge
        extensions (e.g. noise-aware routing), at which point A* begins to
        outperform BFS.

    Args:
        coupling_map: The TesseraCouplingMap to search.
        start:        Starting physical qubit index.
        end:          Goal physical qubit index.

    Returns:
        A list of physical qubit indices forming the shortest path from
        start to end. Has length 1 (just [start]) when start == end.

    Raises:
        ValueError: If no directed path exists from start to end.
'''
import heapq

def a_star_path(coupling_map, start, end):
    if start == end:
        return [start]

    def heuristic(node):
        return coupling_map.distance(node, end)

    open_set = [(heuristic(start), start, [start])]  # (f_score, node, path)
    closed_set = set()
    while open_set:
        f_score, current, path = heapq.heappop(open_set)

        if current in closed_set:
            continue
        closed_set.add(current)

        for neighbor in coupling_map.neighbors(current):
            if neighbor in closed_set:
                continue
            new_path = path + [neighbor]
            if neighbor == end:
                return new_path
            heapq.heappush(open_set, (len(new_path) + heuristic(neighbor), neighbor, new_path))
    
    raise ValueError(f"Tessera: No path exists between q{start} and q{end} in the coupling map")  # pragma: no cover