import time
import heapq
from rich.console import Console
from rich.panel import Panel
import questionary

from helpers.result_helper import show_result, visualize_route
from store.states import GlobalState

console = Console()

class UniformCostSearch:
    def __init__(self, graph: dict):
        """
        Initialize the Uniform Cost Search with a graph.
        """
        self.graph = graph
    
    def search(self, start: str = None, goal: str = None) -> tuple[list[str], int, list]:
        """
        Search route from start to goal using Uniform Cost Search algorithm.
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
        
        # Format: (cost_so_far, location, path_so_far)
        open_list = [(0, start, [start])]
        heapq.heapify(open_list)
        
        best_cost = {start: 0}
        visited = []
        step = 1
        
        if GlobalState.show_process:
            console.print(Panel(f"[bold cyan]ILUSTRASI PROSES PENCARIAN UNIFORM COST SEARCH[/bold cyan]"))
            console.print(f"Mencari rute dari [green]{start}[/green] ke [green]{goal}[/green]...")
        
        while open_list:
            # Get node with lowest cost
            current_cost, current, path = heapq.heappop(open_list)
            
            # Add to visited list (for tracking)
            if current not in visited:
                visited.append(current)
            
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
                return path, current_cost, visited
            
            # Check all neighbors of current node
            if current in graph_dict:
                neighbors_info = []
                
                for neighbor, step_cost in graph_dict[current]:
                    new_cost = current_cost + step_cost
                    
                    if neighbor not in best_cost or new_cost < best_cost[neighbor]:
                        best_cost[neighbor] = new_cost
                        new_path = path + [neighbor]
                        heapq.heappush(open_list, (new_cost, neighbor, new_path))
                        neighbors_info.append((neighbor, step_cost, new_cost))
                
                if GlobalState.show_process and neighbors_info:
                    console.print("  Memeriksa tetangga:")
                    neighbors_info.sort(key=lambda x: x[2])
                    for neighbor, step_cost, new_cost in neighbors_info:
                        console.print(f"     - [blue]{neighbor}[/blue]: Jarak = [yellow]{step_cost}[/yellow] meter, Total biaya = [yellow]{new_cost}[/yellow] meter")
                    
                    if neighbors_info:
                        next_location = neighbors_info[0][0]
                        console.print(f"  Tetangga dengan biaya terendah: [bold cyan]{next_location}[/bold cyan] ([yellow]{neighbors_info[0][2]}[/yellow] meter)")
                
                if GlobalState.show_process and not neighbors_info:
                    console.print(f"  [red]Tidak ada tetangga yang belum dikunjungi dari lokasi {current}.[/red]")
        
        if GlobalState.show_process:
            console.print(Panel("[bold red]TIDAK ADA RUTE![/bold red] Tidak dapat menemukan rute ke tujuan."))
        return None

    def search_multigoal(self) -> tuple[list[str], int, list]:
        """
        Find the route from start to multiple goals using Uniform Cost Search sequentially.
        """
        current_location = GlobalState.start_location
        full_path = [current_location]
        total_cost = 0
        all_visited_nodes = []
        
        if not isinstance(GlobalState.destination_location, list):
            console.print("[bold red]Error: destination_location should be a list for multi-goal search[/bold red]")
            return None
        
        remaining_goals = GlobalState.destination_location.copy()
        
        while remaining_goals:
            # Cari tujuan terdekat dari lokasi saat ini
            nearest_goal = None
            nearest_path = None
            nearest_cost = float('inf')
            nearest_visited = None
            
            for goal in remaining_goals:
                if GlobalState.show_process:
                    console.print(f"\n[bold cyan]Mencoba tujuan: {goal}[/bold cyan]")
                    console.print(f"Dari lokasi saat ini: [green]{current_location}[/green]")
                
                # Cari rute ke tujuan ini
                result = self.search(current_location, goal)
                
                if result is not None:
                    path, cost, visited = result
                    if cost < nearest_cost:
                        nearest_goal = goal
                        nearest_path = path
                        nearest_cost = cost
                        nearest_visited = visited
            
            # Jika tidak ada tujuan yang dapat dicapai, keluar dari loop
            if nearest_goal is None:
                console.print(f"[bold red]Tidak dapat menemukan rute ke tujuan apa pun dari {current_location}[/bold red]")
                return None
            
            # Tambahkan rute terbaik ke path keseluruhan
            if len(full_path) > 0 and len(nearest_path) > 0 and full_path[-1] == nearest_path[0]:
                nearest_path = nearest_path[1:]
            
            full_path.extend(nearest_path)
            total_cost += nearest_cost
            all_visited_nodes.extend(nearest_visited)
            
            # Perbarui lokasi saat ini dan hapus tujuan yang sudah dicapai
            current_location = nearest_goal
            remaining_goals.remove(nearest_goal)
        
        return full_path, total_cost, list(dict.fromkeys(all_visited_nodes))

def run_ucs():
    ucs = UniformCostSearch(GlobalState.malang_graph)
        
    start_time = time.time()
    
    if GlobalState.is_multi:
        result = ucs.search_multigoal()
    else:
        result = ucs.search()
        
    end_time = time.time()
    time_computation = end_time - start_time
    
    if result:  # Check if result is not None
        show_result(result, time_computation)
        
        path, cost, _ = result
        estimated_time = cost / 833.33  # Assume speed is 50 km/h (833.33 m/minutes)
        
        if estimated_time > GlobalState.max_operating_time:
            console.print(f"[bold red]Peringatan: Rute ini membutuhkan waktu {estimated_time:.2f} menit, "
                        f"melebihi batas waktu operasional {GlobalState.max_operating_time} menit![/bold red]")

        if GlobalState.G is not None and GlobalState.location_nodes is not None:
            if questionary.confirm("Apakah Anda ingin melihat visualisasi rute pada peta?").ask():
                visualize_route(path)
    else:
        console.print(Panel("[bold red]Error: Tidak dapat menemukan rute dari titik awal ke tujuan[/bold red]"))