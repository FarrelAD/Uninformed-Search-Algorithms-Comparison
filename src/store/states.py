from dataclasses import dataclass
import networkx as nx

@dataclass
class GlobalState:
    G: nx.MultiDiGraph = None
    malang_graph: list[dict] = None
    location_nodes: list[dict] = None
    start_location: str = None
    destination_location: str|list[str] = None
    max_operating_time: int = 0
    is_multi: bool = False
    show_process: bool = False
    avg_speed: float = 0
