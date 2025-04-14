from init import load_dataset
from pathlib import Path

if __name__ == '__main__':
    print('PROGRAM IS RUNNING')
    
    root_dir = Path(__file__).resolve().parent.parent
    
    graph_file_path = Path(f"{root_dir}/data/java_graph.graphml")
    if not graph_file_path.exists():
        load_dataset()
    