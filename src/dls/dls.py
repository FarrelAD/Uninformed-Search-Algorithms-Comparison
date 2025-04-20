import time
from rich.console import Console
from rich.panel import Panel
import questionary

from helpers.result_helper import show_result, visualize_route
from store.states import GlobalState

console = Console()

def search(max_depth: int, start: str = None, goal: str = None) -> tuple[list[str], int, list[str]]:
    start = start if start is not None else GlobalState.start_location
    goal = goal if goal is not None else GlobalState.destination_location
    
    if GlobalState.show_process:
        console.print(Panel(f"[bold cyan]ILUSTRASI PROSES PENCARIAN DEPTH-LIMITED SEARCH[/bold cyan]"))
        console.print(f"Mencari rute dari [green]{start}[/green] ke [green]{goal}[/green]...")

    current_depth = 0
    path = []
    
    tree = next((node for node in GlobalState.malang_graph if node["node"] == start), None)
    
    is_found = False
    
    def go_deep(tree: dict, depth: int) -> None:
        nonlocal is_found, path
        
        depth += 1
        path.append(tree["node"])
        
        if depth == max_depth:
            print("Depth limit reached!")
            return
        
        for n in tree["branch"]:
            if n["node"] == goal:
                is_found = True
                path.append(n["node"])
                break
            else:
                tree = next((node for node in GlobalState.malang_graph if node["node"] == n["node"]), None)
                go_deep(tree, depth)
    
    go_deep(tree, current_depth)
    
    if is_found:
        print("Found the goal!")
    else:
        print("Goal not found!")
    
    print(f"Path: {path}")
    
    return [], 0, []

def search_multigoal(max_depth: int) -> tuple[list[str], int, list[str]]:
    pass


def run_dls() -> None:
    """
    Execute the Depth Limited Search (DLS) algorithm.
    """
    max_depth = questionary.text(
        "How many max depth do you want to search?",
        validate=lambda text: text.isdigit() and 1 <= int(text) <= 5,
        instruction="Enter the number of destination (1-5): "
    ).ask()
    max_depth = int(max_depth)
    
    start_time = time.time()
    
    if GlobalState.is_multi:
        result = search_multigoal(max_depth)
    else:
        result = search(max_depth)
        
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
