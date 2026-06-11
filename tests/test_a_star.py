'''
    Tests for a_star_path
    ---------------------
    Covers A* pathfinding on linear and disconnected coupling maps using
    coupling_map.distance as the heuristic.
'''
import pytest
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.routing.a_star import a_star_path


def make_linear_map():
    return TesseraCouplingMap(4, [(0, 1), (1, 2), (2, 3)])


def make_bidirectional_map():
    return TesseraCouplingMap(4, [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2)])


def test_direct_path():
    assert a_star_path(make_linear_map(), 0, 1) == [0, 1]


def test_longer_path():
    assert a_star_path(make_linear_map(), 0, 3) == [0, 1, 2, 3]


def test_same_node():
    assert a_star_path(make_linear_map(), 0, 0) == [0]


def test_no_path_raises():
    with pytest.raises(ValueError, match="No path exists"):
        a_star_path(make_linear_map(), 3, 0)


def test_path_starts_at_start():
    assert a_star_path(make_bidirectional_map(), 1, 3)[0] == 1


def test_path_ends_at_end():
    assert a_star_path(make_bidirectional_map(), 0, 2)[-1] == 2


def test_path_length_matches_distance():
    cm = make_bidirectional_map()
    path = a_star_path(cm, 0, 3)
    # Path has N+1 nodes for N edges, so distance == len(path) - 1
    assert len(path) - 1 == cm.distance(0, 3)


def test_path_is_optimal():
    # On a linear graph, the optimal path is the only path.
    cm = make_linear_map()
    path = a_star_path(cm, 0, 3)
    assert path == [0, 1, 2, 3]


def test_revisited_nodes_are_skipped():
    # Diamond with tail: 0->1, 0->2, 1->3, 2->3, 3->4, 4->5. End=5.
    # Node 3 is enqueued via both branches of the diamond before the first
    # copy is popped. The second pop must hit the "already in closed set"
    # skip branch. The diamond endpoint (3) is NOT the goal, so the first
    # processing of 3 doesn't short-circuit via early-return.
    cm = TesseraCouplingMap(6, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5)])
    path = a_star_path(cm, 0, 5)
    assert path[0] == 0
    assert path[-1] == 5
