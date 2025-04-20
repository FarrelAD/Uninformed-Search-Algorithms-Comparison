import time
from rich.console import Console
from rich.panel import Panel
import questionary

from helpers.result_helper import show_result, visualize_route
from store.states import GlobalState

from pprint import pprint

console = Console()

def search(start: str = None, goal: str = None) -> tuple[list[str], int, list[str]]:
    path = []
    visited = []
    
    # preview data malang graph.json yang sudah tersimpan di GlobalState
    pprint(GlobalState.malang_graph) # remove this line if not needed
    
    # TODO: Implement DFS algorithm here
    # This is a placeholder implementation.
    
    return path, 0, visited

def search_multigoal() -> None:
    path = []
    visited = []
    
    # preview data malang graph.json yang sudah tersimpan di GlobalState
    pprint(GlobalState.malang_graph) # remove this line if not needed
    
    # TODO: Implement multi-goal DFS algorithm here
    # This is a placeholder implementation.
    
    return path, 0, visited

def run_dfs() -> tuple[list[str], int, list[str]]:
    """
    Execute the Depth First Search (DFS) algorithm.
    """
    
    start_time = time.time()
    
    if GlobalState.is_multi:
        result = search_multigoal()
    else:
        result = search()
        
    end_time = time.time()
    time_computation = end_time - start_time
    
    show_result(result, time_computation)
    
    if result:
        _, cost, _ = result
        estimated_time = cost / 833.33  # Assume speed is 50 km/h (833.33 m/minutes)
        
        if estimated_time > GlobalState.max_operating_time:
            console.print(f"[bold red]WARNING!: This route takes {estimated_time:.2f} minutes, "
                        f"melebihi batas waktu operasional {GlobalState.max_operating_time} menit![/bold red]")

    if result[0] and GlobalState.G is not None and GlobalState.location_nodes is not None:
        if questionary.confirm("Apakah Anda ingin melihat visualisasi rute pada peta?").ask():
            visualize_route(result[0])
