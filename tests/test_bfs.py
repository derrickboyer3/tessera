'''
    Tests for bfs_path
    ------------------
    Covers BFS pathfinding on linear and disconnected coupling maps.
'''
import pytest
from tessera.hardware.coupling_map import TesseraCouplingMap
from tessera.routing.bfs import bfs_path


def make_linear_map():
    return TesseraCouplingMap(4, [(0, 1), (1, 2), (2, 3)])


def test_bfs_direct_path():
    assert bfs_path(make_linear_map(), 0, 1) == [0, 1]


def test_bfs_longer_path():
    assert bfs_path(make_linear_map(), 0, 3) == [0, 1, 2, 3]


def test_bfs_same_node():
    assert bfs_path(make_linear_map(), 0, 0) == [0]


def test_bfs_no_path_raises():
    # Linear map is directed 0->1->2->3 with no reverse edges
    with pytest.raises(ValueError, match="No path exists"):
        bfs_path(make_linear_map(), 3, 0)


def test_bfs_path_starts_at_start():
    assert bfs_path(make_linear_map(), 1, 3)[0] == 1


def test_bfs_path_ends_at_end():
    assert bfs_path(make_linear_map(), 0, 2)[-1] == 2
