from dataclasses import dataclass
import networkx as nx

@dataclass
class GlobalState:
    G: nx.MultiDiGraph = None
    malang_graph: dict = None
    location_nodes: dict = None
    start_location: str = None
    destination_location: str|list = None
    max_operating_time: int = 0
    is_multi: bool = False
