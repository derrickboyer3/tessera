'''
    Tests for ROUTING_REGISTRY
    --------------------------
    Covers registry contents, strategy wrapping, and the whole-circuit
    contract returned by each entry.
'''
from tessera.routing.routing_registry import ROUTING_REGISTRY
from tessera.routing.sabre import sabre_route
from tessera.circuit import TesseraCircuit
from tessera.instruction import TesseraInstruction
from tessera.hardware.coupling_map import TesseraCouplingMap


def make_coupling_map():
    return TesseraCouplingMap(4, [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2)])


def make_routable_circuit():
    return TesseraCircuit(4, 0, [
        TesseraInstruction("cx", [0, 3], [], []),
    ], layout={0: 0, 1: 1, 2: 2, 3: 3})


def test_registry_contains_bfs():
    assert "bfs" in ROUTING_REGISTRY


def test_registry_contains_a_star():
    assert "a_star" in ROUTING_REGISTRY


def test_registry_contains_sabre():
    assert "sabre" in ROUTING_REGISTRY


def test_sabre_entry_is_sabre_route():
    assert ROUTING_REGISTRY["sabre"] is sabre_route


def test_all_entries_are_callable():
    for fn in ROUTING_REGISTRY.values():
        assert callable(fn)


def test_all_entries_return_circuit():
    for name, fn in ROUTING_REGISTRY.items():
        result = fn(make_routable_circuit(), make_coupling_map())
        assert isinstance(result, TesseraCircuit), f"{name} did not return a TesseraCircuit"


def test_all_entries_route_non_adjacent_with_swaps():
    cm = make_coupling_map()
    for name, fn in ROUTING_REGISTRY.items():
        result = fn(make_routable_circuit(), cm)
        names = [ins.name for ins in result.instructions]
        assert "swap" in names, f"{name} did not insert any swaps for non-adjacent cx"
