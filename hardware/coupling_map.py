'''
    Tessera Coupling Map
    --------------------
    Represents the physical qubit connectivity of a quantum backend as a directed graph.
    Each node is a physical qubit and each directed edge represents an allowed two-qubit
    gate direction between qubits (e.g. cx(q0, q1) is only valid if edge q0->q1 exists).

    Internally uses networkx DiGraph as the graph engine. All methods expose a clean
    interface so the rest of the transpiler never interacts with networkx directly,
    making the graph backend swappable in the future.

    Methods:
        add_edge(start, end)         — add a directed connection between two qubits
        are_connected(start, end)    — check if a directed edge exists from start to end
        neighbors(q)                 — get all qubits that q can directly drive a gate to
        shortest_path(start, end)    — shortest hop path between two qubits
        distance(start, end)         — number of hops between two qubits
        is_valid_qubit(q)            — check if a qubit index exists in the coupling map
        edges                        — property returning all directed edges as a list
        __len__                      — returns the number of qubits in the coupling map
        __repr__                     — returns a readable string representation for debugging

    Raises:
        ValueError: If a path or node does not exist in the coupling map.
'''
import networkx as nx

class TesseraCouplingMap():
    def __init__(self, num_qubits, edges=None):
        self.num_qubits = num_qubits
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(range(num_qubits))
        if edges is not None:
            for edge in edges:
                self.graph.add_edge(edge[0], edge[1])

    def add_edge(self, start, end):
        if self.graph.has_edge(start, end):
            print(f"[Tessera] Coupling Map already has edge from q{start}->q{end}.")
            return
        self.graph.add_edge(start, end)
            
    def are_connected(self, start, end):
        return self.graph.has_edge(start, end)

    def neighbors(self, q):
        return list(self.graph.neighbors(q))

    def shortest_path(self, start, end):
        try:
            return nx.shortest_path(self.graph, start, end)
        except nx.NetworkXNoPath:
            raise ValueError(f"Tessera: No path exists between q{start} and q{end} in the coupling map")
        except nx.NodeNotFound:
            raise ValueError(f"Tessera: One or both qubits q{start}, q{end} do not exist in the coupling map")

    def distance(self, start, end):
        try:
            return nx.shortest_path_length(self.graph, start, end)
        except nx.NetworkXNoPath:
            raise ValueError(f"Tessera: No path exists between q{start} and q{end} in the coupling map")
        except nx.NodeNotFound:
            raise ValueError(f"Tessera: One or both qubits q{start}, q{end} do not exist in the coupling map")

    def is_valid_qubit(self, q):
        return self.graph.has_node(q)

    def __len__(self):
        return self.num_qubits
    
    def __repr__(self):
        return f"TesseraCouplingMap(num_qubits={self.num_qubits}, edges={list(self.graph.edges())})"

    @property
    def edges(self):
        return list(self.graph.edges())