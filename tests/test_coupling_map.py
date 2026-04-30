from tessera.hardware.coupling_map import TesseraCouplingMap
import pytest

def make_linear_map():
    # 0->1->2->3
    return TesseraCouplingMap(4, [(0,1), (1,2), (2,3)])

def test_num_qubits():
    cm = make_linear_map()
    assert cm.num_qubits == 4

def test_len():
    cm = make_linear_map()
    assert len(cm) == 4

def test_edges_on_init():
    cm = make_linear_map()
    assert (0, 1) in cm.edges
    assert (1, 2) in cm.edges
    assert (2, 3) in cm.edges

def test_no_edges_on_empty_init():
    cm = TesseraCouplingMap(3)
    assert cm.edges == []

def test_add_edge():
    cm = TesseraCouplingMap(3)
    cm.add_edge(0, 1)
    assert (0, 1) in cm.edges

def test_add_duplicate_edge_does_not_add():
    cm = TesseraCouplingMap(3, [(0, 1)])
    cm.add_edge(0, 1)
    assert cm.edges.count((0, 1)) == 1

def test_are_connected_true():
    cm = make_linear_map()
    assert cm.are_connected(0, 1) == True

def test_are_connected_false_no_edge():
    cm = make_linear_map()
    assert cm.are_connected(0, 2) == False

def test_are_connected_respects_direction():
    cm = make_linear_map()
    assert cm.are_connected(1, 0) == False

def test_neighbors():
    cm = make_linear_map()
    assert cm.neighbors(1) == [2]

def test_neighbors_no_outgoing():
    cm = make_linear_map()
    assert cm.neighbors(3) == []

def test_shortest_path():
    cm = make_linear_map()
    assert cm.shortest_path(0, 3) == [0, 1, 2, 3]

def test_shortest_path_no_path_raises():
    cm = make_linear_map()
    with pytest.raises(ValueError, match="No path exists"):
        cm.shortest_path(3, 0)

def test_shortest_path_invalid_qubit_raises():
    cm = make_linear_map()
    with pytest.raises(ValueError, match="do not exist"):
        cm.shortest_path(0, 99)

def test_distance():
    cm = make_linear_map()
    assert cm.distance(0, 3) == 3

def test_distance_no_path_raises():
    cm = make_linear_map()
    with pytest.raises(ValueError, match="No path exists"):
        cm.distance(3, 0)

def test_is_valid_qubit_true():
    cm = make_linear_map()
    assert cm.is_valid_qubit(0) == True

def test_is_valid_qubit_false():
    cm = make_linear_map()
    assert cm.is_valid_qubit(99) == False

def test_distance_invalid_qubit_raises():
    cm = make_linear_map()
    with pytest.raises(ValueError, match="do not exist"):
        cm.distance(0, 99)

def test_repr():
    cm = TesseraCouplingMap(2, [(0, 1)])
    assert repr(cm) == "TesseraCouplingMap(num_qubits=2, edges=[(0, 1)])"