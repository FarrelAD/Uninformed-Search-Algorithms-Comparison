import time
from rich.console import Console
from rich.panel import Panel
import questionary
from collections import deque

from helpers.result_helper import show_result, visualize_route
from store.states import GlobalState

console = Console()

class BreadthFirstSearch:
    def __init__(self, graph: list):
        """
        Initialize the Breadth First Search with a graph.
        """
        self.graph = graph
    
    def search(self, start: str = None, goal: str = None) -> tuple[list[str], int, int]:
        """
        Search route from start to goal using Breadth First Search algorithm.
        """
        start = start if start is not None else GlobalState.start_location
        goal = goal if goal is not None else GlobalState.destination_location
        
        # Transform graph into an adjacency dict for easier processing
        graph_dict = {}
        for node_data in self.graph:
            node_name = node_data["node"]
            neighbors = []
            for branch in node_data.get("branch", []):
                neighbors.append((branch["node"], branch["distance"]))
            graph_dict[node_name] = neighbors
        
        # Format: (location, path_so_far, cost_so_far)
        queue = deque([(start, [start], 0)])
        visited = {start}  # Set of visited nodes
        visited_count = 0  # Count of steps for tracking
        step = 1
        
        if GlobalState.show_process:
            console.print(Panel(f"[bold cyan]ILUSTRASI PROSES PENCARIAN BREADTH FIRST SEARCH[/bold cyan]"))
            console.print(f"Mencari rute dari [green]{start}[/green] ke [green]{goal}[/green]...")
        
        while queue:
            # Get node from the queue (FIFO)
            current, path, current_cost = queue.popleft()
            visited_count += 1
            
            if GlobalState.show_process:
                console.print(f"\n[bold]Langkah {step}:[/bold]")
                console.print(f"  Mengunjungi lokasi: [cyan]{current}[/cyan]")
                console.print(f"  Biaya sejauh ini: [yellow]{current_cost} (meter)[/yellow]")
                console.print(f"  Rute sejauh ini: [green]{' -> '.join(path)}[/green]")
                step += 1
                time.sleep(0.3)
            
            # If goal reached, return path and cost
            if current == goal:
                if GlobalState.show_process:
                    console.print(Panel("[bold green]TUJUAN TERCAPAI![/bold green] Lokasi tujuan telah ditemukan."))
                return path, current_cost, visited_count
            
            # Check all neighbors of current node
            if current in graph_dict:
                neighbors_info = []
                
                for neighbor, step_cost in graph_dict[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_cost = current_cost + step_cost
                        new_path = path + [neighbor]
                        queue.append((neighbor, new_path, new_cost))
                        neighbors_info.append((neighbor, step_cost, new_cost))
                
                if GlobalState.show_process and neighbors_info:
                    console.print("  Memeriksa tetangga:")
                    for neighbor, step_cost, new_cost in neighbors_info:
                        console.print(f"     - [blue]{neighbor}[/blue]: Jarak = [yellow]{step_cost}[/yellow] meter, Total biaya = [yellow]{new_cost}[/yellow] meter")
                    
                if GlobalState.show_process and not neighbors_info:
                    console.print(f"  [red]Tidak ada tetangga yang belum dikunjungi dari lokasi {current}.[/red]")
        
        if GlobalState.show_process:
            console.print(Panel("[bold red]TIDAK ADA RUTE![/bold red] Tidak dapat menemukan rute ke tujuan."))
        
        # Return None if no path found (will be handled by the caller)
        return [], 0, visited_count

    def search_multigoal(self) -> list[tuple[list[str], int, int]] | None:
        """
        Run multigoal/destination search.
        """
        result = []
        start = GlobalState.start_location
        iteration = 0
        
        # Create a copy of the destination_location list to avoid modifying the original
        destinations = GlobalState.destination_location.copy()

        while len(destinations) > 0:
            iteration += 1
            destination = destinations.pop(0)

            if GlobalState.show_process:
                console.print(f"\n[bold cyan]Searching for destination number-{iteration}: {destination}[/bold cyan]")
                console.print(f"From: [green]{start}[/green]")

            search_result = self.search(start, destination)
            if not search_result[0]:  # Check if path is empty
                if GlobalState.show_process:
                    console.print(Panel(f"[bold red]Gagal menemukan rute ke tujuan: {destination}[/bold red]"))
                return None  # Stop if any destination cannot be reached

            result.append(search_result)
            start = destination  # Next start = previous goal

        return result

def run_bfs():
    """
    Execute the Breadth First Search (BFS) algorithm.
    """
    bfs = BreadthFirstSearch(GlobalState.malang_graph)
        
    start_time = time.time()
    
    if GlobalState.is_multi:
        result = bfs.search_multigoal()
    else:
        result = bfs.search()
        
    end_time = time.time()
    time_computation = end_time - start_time

    show_result("BFS", result, time_computation)
    
    if result:
        if GlobalState.is_multi:
            sum_distance = 0
            for r in result:
                path, distance, _ = r
                sum_distance += distance
            estimated_time = sum_distance / 833.33
        else:
            path, distance, _ = result
            estimated_time = distance / 833.33  # Assume speed is 50 km/h (833.33 m/minutes)
        
        if estimated_time > GlobalState.max_operating_time:
            console.print(f"[bold red]WARNING!: This route takes {estimated_time:.2f} minutes, "
                        f"melebihi batas waktu operasional {GlobalState.max_operating_time} menit![/bold red]")

        if questionary.confirm("Apakah Anda ingin melihat visualisasi rute pada peta?").ask():
            if GlobalState.is_multi:
                # For multi-goal, we need to extract and combine all paths
                combined_path = []
                for r in result:
                    path, _, _ = r
                    if combined_path and combined_path[-1] == path[0]:
                        # Avoid duplicating connecting points between segments
                        combined_path.extend(path[1:])
                    else:
                        combined_path.extend(path)
                visualize_route(combined_path)
            else:
                # For single goal, we just pass the path
                path, _, _ = result
                visualize_route(path)
                
    return result