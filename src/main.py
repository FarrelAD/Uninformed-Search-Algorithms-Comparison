import questionary
from pathlib import Path
from init import load_dataset
import bfs
import dfs
import ucs
import dls

if __name__ == '__main__':
    print('PROGRAM IS RUNNING')
    
    root_dir = Path(__file__).resolve().parent.parent
    
    graph_file_path = Path(f"{root_dir}/data/java_graph.graphml")
    if not graph_file_path.exists():
        load_dataset()
    
    algorithm_selection = questionary.select(
        "Select algorithm to run:",
        choices=[
            "Breadth-First Search (BFS)",
            "Depth-First Search (DFS)",
            "Uniform Cost Search (UCS)",
            "Depth Limited Search (DLS)",
        ]
    ).ask()
    
    if algorithm_selection == "Breadth-First Search (BFS)":
        bfs.run()
    elif algorithm_selection == "Depth-First Search (DFS)":
        dfs.run()
    elif algorithm_selection == "Uniform Cost Search (UCS)":
        ucs.run()
    elif algorithm_selection == "Depth Limited Search (DLS)":
        dls.run()