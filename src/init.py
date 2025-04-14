import osmnx as ox
from pathlib import Path

def load_dataset():
    print('Loading dataset...')
    graph = ox.graph_from_place("Malang, Indonesia", network_type='drive')
    
    root_dir = Path(__file__).resolve().parent.parent
    
    ox.save_graphml(graph, filepath=f"{root_dir}/data/java_graph.graphml", encoding='utf-8')
    print("Graph saved to data/java_graph.graphml")
