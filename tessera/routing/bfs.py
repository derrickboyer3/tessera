'''
    BFS Pathfinding
    ---------------
    Breadth-first search over the coupling map's directed graph. Returns the
    shortest hop path between two physical qubits as a list of nodes
    (inclusive on both ends). Used as the default pairwise path finder for
    routing.

    The algorithm is the obvious one: maintain a queue of paths, expand the
    head of each, return the first path that reaches the target. Because
    every edge has unit cost, BFS guarantees the shortest hop count.

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
def bfs_path(coupling_map, start, end):
    if start == end:
        return [start]
    
    visited = {start}
    queue = [[start]]  # queue of paths, not just nodes
    
    while queue:
        path = queue.pop(0)
        current = path[-1]
        
        for neighbor in coupling_map.neighbors(current):
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    
    raise ValueError(f"Tessera: No path exists between q{start} and q{end} in the coupling map")