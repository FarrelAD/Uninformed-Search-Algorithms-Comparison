import time
import heapq
from rich.console import Console
from rich.panel import Panel
import questionary

from helpers.result_helper import show_result, visualize_route
from store.states import GlobalState

console = Console()

class UniformCostSearch:
    def __init__(self, graph):
        """
        Inisialisasi algoritma Uniform Cost Search.
        
        Args:
            graph: Dictionary berisi graph dengan lokasi sebagai kunci dan daftar tetangga beserta bobot
        """
        self.graph = graph
    
    def search(self, show_process: bool, start: str = None, goal: str = None) -> tuple[list[str], int, list]:
        """
        Melakukan pencarian rute dari start ke goal menggunakan Uniform Cost Search.
        
        Args:
            start: Lokasi awal
            goal: Lokasi tujuan
            show_process: Boolean, apakah menampilkan proses pencarian
            
        Returns:
            Tuple (path, total_cost, visited_nodes) jika rute ditemukan, None jika tidak ada rute
        """
        start = start if start is not None else GlobalState.start_location
        goal = goal if goal is not None else GlobalState.destination_location
        
        # Format: (biaya_sejauh_ini, lokasi, path_sejauh_ini)
        print(f"DEBUG! Start: {start}, Goal: {goal}")
        print(f"GlobalState: {GlobalState.start_location}")
        
        open_list = [(0, start, [start])]
        heapq.heapify(open_list)
        
        best_cost = {start: 0}
        
        visited = []
        
        step = 1
        
        if show_process:
            console.print(Panel(f"[bold cyan]ILUSTRASI PROSES PENCARIAN UNIFORM COST SEARCH[/bold cyan]"))
            console.print(f"Mencari rute dari [green]{start}[/green] ke [green]{goal}[/green]...")
        
        while open_list:
            # Ambil simpul dengan biaya terendah
            current_cost, current, path = heapq.heappop(open_list)
            
            # Tambahkan ke daftar yang dikunjungi (untuk pelacakan)
            if current not in visited:
                visited.append(current)
            
            if show_process:
                console.print(f"\n[bold]Langkah {step}:[/bold]")
                console.print(f"  Mengunjungi lokasi: [cyan]{current}[/cyan]")
                console.print(f"  Biaya sejauh ini: [yellow]{current_cost} (meter)[/yellow]")
                console.print(f"  Rute sejauh ini: [green]{' -> '.join(path)}[/green]")
                step += 1
                time.sleep(0.3)  # Pause sebentar agar pengguna dapat membaca
            
            # Jika sudah mencapai tujuan, kembalikan path dan biaya
            if current == goal:
                if show_process:
                    console.print(Panel("[bold green]TUJUAN TERCAPAI![/bold green] Lokasi tujuan telah ditemukan."))
                return path, current_cost, visited
            
            # Cek semua tetangga dari simpul saat ini
            if current in self.graph:
                neighbors_info = []
                
                for neighbor, step_cost in self.graph[current]:
                    new_cost = current_cost + step_cost
                    
                    if neighbor not in best_cost or new_cost < best_cost[neighbor]:
                        best_cost[neighbor] = new_cost
                        new_path = path + [neighbor]
                        heapq.heappush(open_list, (new_cost, neighbor, new_path))
                        neighbors_info.append((neighbor, step_cost, new_cost))
                
                if show_process and neighbors_info:
                    console.print("  Memeriksa tetangga:")
                    neighbors_info.sort(key=lambda x: x[2])
                    for neighbor, step_cost, new_cost in neighbors_info:
                        console.print(f"     - [blue]{neighbor}[/blue]: Jarak = [yellow]{step_cost}[/yellow] meter, Total biaya = [yellow]{new_cost}[/yellow] meter")
                    
                    if neighbors_info:
                        next_location = neighbors_info[0][0]
                        console.print(f"  Tetangga dengan biaya terendah: [bold cyan]{next_location}[/bold cyan] ([yellow]{neighbors_info[0][2]}[/yellow] meter)")
                
                if show_process and not neighbors_info:
                    console.print(f"  [red]Tidak ada tetangga yang belum dikunjungi dari lokasi {current}.[/red]")
        
        if show_process:
            console.print(Panel("[bold red]TIDAK ADA RUTE![/bold red] Tidak dapat menemukan rute ke tujuan."))
        return None

    def search_multigoal(self, show_process: bool) -> tuple[list[str], int, list]:
        """
        Melakukan pencarian rute dari start ke multiple goals menggunakan Uniform Cost Search secara berurutan.
        """
        current_location = GlobalState.start_locationt
        full_path = [GlobalState.start_location]
        total_cost = 0
        all_visited_nodes = []
        
        for i, goal in enumerate(GlobalState.destination_location):
            if show_process:
                console.print(f"\n[bold cyan]Pencarian tujuan ke-{i+1}: {goal}[/bold cyan]")
                console.print(f"Dari lokasi saat ini: [green]{current_location}[/green]")
            
            # Cari rute ke tujuan berikutnya
            result = self.search(current_location, goal, show_process)
            
            if result is None:
                console.print(f"[bold red]Tidak dapat menemukan rute ke {goal} dari {current_location}[/bold red]")
                return None
            
            path, cost, visited = result
            
            # Update informasi rute secara keseluruhan
            # Tambahkan semua node kecuali node awal (karena sudah ada di full_path)
            full_path.extend(path[1:])
            total_cost += cost
            all_visited_nodes.extend(visited)
            
            current_location = goal
        
        return full_path, total_cost, list(set(all_visited_nodes))  # Remove duplicate visited nodes

def run_ucs(show_process: bool):
    ucs = UniformCostSearch(GlobalState.malang_graph)
        
    start_time = time.time()
    
    if GlobalState.is_multi:
        result = ucs.search_multigoal(show_process)
    else:
        result = ucs.search(show_process)
        
    end_time = time.time()
    time_computation = end_time - start_time
    
    show_result(result, time_computation)
    
    if result:
        _, cost, _ = result
        estimated_time = cost / 833.33  # Assume speed is 50 km/h (833.33 m/minutes)
        
        if estimated_time > GlobalState.max_operating_time:
            console.print(f"[bold red]Peringatan: Rute ini membutuhkan waktu {estimated_time:.2f} menit, "
                        f"melebihi batas waktu operasional {GlobalState.max_operating_time} menit![/bold red]")

    if result[0] and GlobalState.G is not None and GlobalState.location_nodes is not None:
        if questionary.confirm("Apakah Anda ingin melihat visualisasi rute pada peta?").ask():
            visualize_route(result[0])