import time
from rich.console import Console
from rich.panel import Panel
import questionary

from helpers.result_helper import show_result, visualize_route
from store.states import GlobalState

console = Console()

def search(max_depth: int, start: str = None, goal: str = None) -> tuple[list[str], float, int]:
    """
    Run single destination search
    """
    start = start if start is not None else GlobalState.start_location
    goal = goal if goal is not None else GlobalState.destination_location
    
    if GlobalState.show_process:
        console.print(Panel(f"[bold cyan]ILLUSTRATION OF SEARCH PROCESS DEPTH-LIMITED SEARCH[/bold cyan]"))
        console.print(f"Mencari rute dari [green]{start}[/green] ke [green]{goal}[/green]...")

    current_depth = 0
    path = []
    visited = 0
    
    tree = next((node for node in GlobalState.malang_graph if node["node"] == start), None)
    
    is_found = False
    
    def go_deep(tree: dict, depth: int, prev_node: str = None, distance: float = 0) -> None:
        """
        Recursion function to get the correct path
        """
        nonlocal is_found, path, visited
        
        depth += 1
        path.append({
            "name": tree["node"],
            "distance": distance,
        })
        visited += 1
        
        if is_found:
            return True
        
        if depth > max_depth:
            path.pop()
            return False
        
        if tree["node"] == goal:
            is_found = True
            return True
        
        branch = [n for n in tree["branch"] if n["node"] != prev_node]
        for n in branch:
            prev_node = tree["node"]
            distance = n["distance"]
            tree = next((node for node in GlobalState.malang_graph if node["node"] == n["node"]), None)
            result = go_deep(tree, depth, prev_node, distance)
            
            if result:
                return True
        
        return False
    
    go_deep(tree, current_depth)
    
    if is_found:
        print("Found the goal!")
    else:
        print("Goal not found!")
    
    total_distance = sum([p["distance"] for p in path]) if is_found else 0
    all_path = [p["name"] for p in path] if is_found else ["Not found"]
    
    return all_path, total_distance, visited

def search_multigoal(max_depth: int) -> list[tuple[list[str], float, int]]:
    """
    Run multigoal/destination search
    """
    result = []
    
    start = GlobalState.start_location
    iteration = 0
    while len(GlobalState.destination_location) > 0:
        iteration += 1 
        destination = GlobalState.destination_location.pop(0)
        
        if GlobalState.show_process:
            console.print(f"\n[bold cyan]Searching for destination number-{iteration}: {destination}[/bold cyan]")
            console.print(f"From: [green]{start}[/green]")
        
        result.append(search(max_depth, start, destination))
        start = destination
    
    return result


def run_dls() -> None:
    """
    Execute the Depth Limited Search (DLS) algorithm.
    """
    max_depth = questionary.text(
        "How many max depth do you want to search?",
        validate=lambda text: text.isdigit() and int(text) > 1,
    ).ask()
    max_depth = int(max_depth)
    
    start_time = time.time()
    
    if GlobalState.is_multi:
        result = search_multigoal(max_depth)
    else:
        result = search(max_depth)
        
    end_time = time.time()
    time_computation = end_time - start_time
    
    show_result("DLS", result, time_computation)
    
    if GlobalState.is_multi:
        sum_distance = 0
        for i, r in enumerate(result):
            _, distance, _ = r
            sum_distance += distance
    else:
        _, distance, _ = result
    
    estimated_time = sum_distance if GlobalState.is_multi else distance / 833.33 # Assume speed is 50 km/h (833.33 m/minutes)
    
    if estimated_time > GlobalState.max_operating_time:
        console.print(f"[bold red]WARNING!: This route takes {estimated_time:.2f} minutes, "
                        f"melebihi batas waktu operasional {GlobalState.max_operating_time} menit![/bold red]")

    if questionary.confirm("Apakah Anda ingin melihat visualisasi rute pada peta?").ask():
        visualize_route(result[0])
