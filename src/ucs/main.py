import time
import datetime
import os
import heapq
import folium
import questionary
import networkx as nx
import osmnx as ox
import pickle
from pathlib import Path
import matplotlib.pyplot as plt
from tabulate import tabulate
from colorama import Fore, Style, init
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from pyfiglet import Figlet

# Inisialisasi colorama
init(autoreset=True)
console = Console()

class UniformCostSearch:
    def __init__(self, graph):
        """
        Inisialisasi algoritma Uniform Cost Search.
        
        Args:
            graph: Dictionary berisi graph dengan lokasi sebagai kunci dan daftar tetangga beserta bobot
        """
        self.graph = graph
    
    def search(self, start, goal, show_process=False):
        """
        Melakukan pencarian rute dari start ke goal menggunakan Uniform Cost Search.
        
        Args:
            start: Lokasi awal
            goal: Lokasi tujuan
            show_process: Boolean, apakah menampilkan proses pencarian
            
        Returns:
            Tuple (path, total_cost, visited_nodes) jika rute ditemukan, None jika tidak ada rute
        """
        # Antrian prioritas untuk simpul yang akan dikunjungi
        # Format: (biaya_sejauh_ini, lokasi, path_sejauh_ini)
        open_list = [(0, start, [start])]
        heapq.heapify(open_list)
        
        # Dictionary untuk menyimpan biaya terbaik ke setiap node
        best_cost = {start: 0}
        
        # Kumpulan simpul yang telah dikunjungi untuk pelacakan
        visited = []
        
        # Langkah untuk visualisasi proses
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
                    # Hitung biaya baru
                    new_cost = current_cost + step_cost
                    
                    # Jika neighbor belum pernah dikunjungi atau ditemukan jalur yang lebih baik
                    if neighbor not in best_cost or new_cost < best_cost[neighbor]:
                        best_cost[neighbor] = new_cost
                        # Buat path baru
                        new_path = path + [neighbor]
                        # Tambahkan ke open list dengan prioritas berdasarkan biaya
                        heapq.heappush(open_list, (new_cost, neighbor, new_path))
                        # Kumpulkan informasi tetangga untuk ditampilkan
                        neighbors_info.append((neighbor, step_cost, new_cost))
                
                # Tampilkan informasi tetangga
                if show_process and neighbors_info:
                    console.print("  Memeriksa tetangga:")
                    # Urutkan tetangga berdasarkan biaya baru
                    neighbors_info.sort(key=lambda x: x[2])
                    for neighbor, step_cost, new_cost in neighbors_info:
                        console.print(f"     - [blue]{neighbor}[/blue]: Jarak = [yellow]{step_cost}[/yellow] meter, Total biaya = [yellow]{new_cost}[/yellow] meter")
                    
                    # Tunjukkan tetangga mana yang akan dikunjungi berikutnya
                    if neighbors_info:
                        next_location = neighbors_info[0][0]
                        console.print(f"  Tetangga dengan biaya terendah: [bold cyan]{next_location}[/bold cyan] ([yellow]{neighbors_info[0][2]}[/yellow] meter)")
                
                if show_process and not neighbors_info:
                    console.print(f"  [red]Tidak ada tetangga yang belum dikunjungi dari lokasi {current}.[/red]")
        
        # Jika tidak ada rute yang ditemukan
        if show_process:
            console.print(Panel("[bold red]TIDAK ADA RUTE![/bold red] Tidak dapat menemukan rute ke tujuan."))
        return None

    def search_multigoal(self, start, goals, show_process=False):
        """
        Melakukan pencarian rute dari start ke multiple goals menggunakan Uniform Cost Search secara berurutan.
        
        Args:
            start: Lokasi awal
            goals: List lokasi tujuan
            show_process: Boolean, apakah menampilkan proses pencarian
            
        Returns:
            Tuple (full_path, total_cost, all_visited_nodes) jika rute ditemukan, None jika tidak ada rute
        """
        current_location = start
        full_path = [start]
        total_cost = 0
        all_visited_nodes = []
        
        # Proses setiap tujuan secara berurutan
        for i, goal in enumerate(goals):
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
            
            # Update lokasi saat ini untuk tujuan berikutnya
            current_location = goal
        
        return full_path, total_cost, list(set(all_visited_nodes))  # Remove duplicate visited nodes
    

def save_osm_data(G, filename="malang_osm_data.pkl"):
    """
    Menyimpan data OSM ke file lokal
    """
    try:
        # Buat direktori data jika belum ada
        data_dir = "osm_data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        filepath = os.path.join(data_dir, filename)
        
        # Simpan graph ke file pickle
        with open(filepath, 'wb') as f:
            pickle.dump(G, f)
        
        console.print(f"[green]Data OSM berhasil disimpan ke [bold]{filepath}[/bold][/green]")
        return True
    except Exception as e:
        console.print(f"[red]Error saat menyimpan data OSM: {str(e)}[/red]")
        return False

def load_osm_data_from_file(filename="malang_osm_data.pkl"):
    """
    Memuat data OSM dari file lokal
    """
    try:
        data_dir = "osm_data"
        filepath = os.path.join(data_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                G = pickle.load(f)
            console.print(f"[green]Data OSM berhasil dimuat dari [bold]{filepath}[/bold][/green]")
            return G
        else:
            console.print(f"[yellow]File data OSM tidak ditemukan: {filepath}[/yellow]")
            return None
    except Exception as e:
        console.print(f"[red]Error saat memuat data OSM dari file: {str(e)}[/red]")
        return None

def load_malang_osm_data():
    """
    Memuat data OpenStreetMap untuk wilayah Malang Raya
    Mencoba memuat dari cache terlebih dahulu, jika tidak ada maka ambil dari OSM
    """
    # Coba memuat dari file lokal terlebih dahulu
    G = load_osm_data_from_file()
    
    if G is not None:
        # Jika berhasil memuat dari file lokal
        try:
            # Lanjutkan dengan membuat graph_dict dan location_nodes
            # Definisikan beberapa lokasi penting di Malang Raya berdasarkan OSM
            important_locations = {
                "Alun-Alun Malang": (-7.9825, 112.6297),
                "Stasiun Malang": (-7.9773, 112.6370),
                "Mall Olympic Garden": (-7.9767, 112.6320),
                "Universitas Brawijaya": (-7.9536, 112.6142),
                "Universitas Negeri Malang": (-7.9621, 112.6186),
                "RS Saiful Anwar": (-7.9677, 112.6361),
                "Balai Kota Malang": (-7.9780, 112.6343),
                "Terminal Arjosari": (-7.9192, 112.6465),
                "Stadion Kanjuruhan": (-8.0342, 112.6217),
                "Jatim Park 1": (-7.8888, 112.5261),
                "Jatim Park 2": (-7.8876, 112.5241),
                "Museum Angkut": (-7.8782, 112.5225),
                "Alun-Alun Batu": (-7.8719, 112.5242),
                "Selecta": (-7.8364, 112.5252),
                "Kampung Wisata Jodipan": (-7.9832, 112.6417),
                "Taman Rekreasi Sengkaling": (-7.9183, 112.5894),
                "Pasar Besar Malang": (-7.9823, 112.6329),
                "Tugu Malang": (-7.9769, 112.6373),
                "Coban Rondo": (-7.8848, 112.4773),
                "Kampus UMM": (-7.9182, 112.5970)
            }
            
            # Temukan node OSM terdekat untuk setiap lokasi penting
            location_nodes = {}
            for name, coords in important_locations.items():
                # Format yang benar: X=longitude, Y=latitude
                nearest_node = ox.distance.nearest_nodes(G, X=coords[1], Y=coords[0])
                location_nodes[name] = nearest_node
            
            # Buat graph khusus dengan bobot jarak
            G_undirected = nx.Graph(G)
            graph_dict = {}
            for name, node_id in location_nodes.items():
                graph_dict[name] = []
                
                # Cari jalur ke semua lokasi lain
                for other_name, other_node_id in location_nodes.items():
                    if name != other_name:
                        try:
                            # Cari rute terpendek antara dua node
                            route = nx.shortest_path(G_undirected, node_id, other_node_id, weight='length')
                            
                            # Hitung total jarak rute
                            distance = sum(G_undirected[u][v]['length'] for u, v in zip(route[:-1], route[1:]))
                            
                            # Tambahkan ke graph
                            graph_dict[name].append((other_name, distance))
                        except nx.NetworkXNoPath:
                            # Jika tidak ada jalur, abaikan
                            console.print(f"[yellow]Tidak ada jalur dari {name} ke {other_name}[/yellow]")
                            pass
                        except Exception as e:
                            console.print(f"[yellow]Error mencari jalur dari {name} ke {other_name}: {str(e)}[/yellow]")
                            pass
            
            console.print("[green]Data OSM berhasil dimuat dari cache lokal![/green]")
            return G, graph_dict, location_nodes
            
        except Exception as e:
            console.print(f"[yellow]Error saat memproses data OSM dari cache: {str(e)}. Mencoba memuat ulang dari OSM...[/yellow]")
            # Lanjutkan ke blok berikutnya untuk memuat dari OSM
    
    # Jika tidak berhasil memuat dari file lokal, ambil dari OSM
    try:
        console.print("[yellow]Memuat data OSM untuk Malang Raya dari internet...[/yellow]")
        
        # Coba mendapatkan data dari OpenStreetMap dengan parameters yang lebih spesifik
        G = ox.graph_from_place("Malang, East Java, Indonesia", network_type="drive", simplify=True)
        
        # Tambahkan edge lengths jika belum ada
        if not 'length' in list(G.edges(data=True))[0][2]:
            G = ox.add_edge_lengths(G)
        
        # Simpan data OSM ke file lokal untuk penggunaan mendatang
        save_osm_data(G)
        
        # Ubah ke graph bidirectional dengan bobot jarak di meter
        G_undirected = nx.Graph(G)
        
        # Definisikan beberapa lokasi penting di Malang Raya berdasarkan OSM
        important_locations = {
            "Alun-Alun Malang": (-7.9825, 112.6297),
            "Stasiun Malang": (-7.9773, 112.6370),
            "Mall Olympic Garden": (-7.9767, 112.6320),
            "Universitas Brawijaya": (-7.9536, 112.6142),
            "Universitas Negeri Malang": (-7.9621, 112.6186),
            "RS Saiful Anwar": (-7.9677, 112.6361),
            "Balai Kota Malang": (-7.9780, 112.6343),
            "Terminal Arjosari": (-7.9192, 112.6465),
            "Stadion Kanjuruhan": (-8.0342, 112.6217),
            "Jatim Park 1": (-7.8888, 112.5261),
            "Jatim Park 2": (-7.8876, 112.5241),
            "Museum Angkut": (-7.8782, 112.5225),
            "Alun-Alun Batu": (-7.8719, 112.5242),
            "Selecta": (-7.8364, 112.5252),
            "Kampung Wisata Jodipan": (-7.9832, 112.6417),
            "Taman Rekreasi Sengkaling": (-7.9183, 112.5894),
            "Pasar Besar Malang": (-7.9823, 112.6329),
            "Tugu Malang": (-7.9769, 112.6373),
            "Coban Rondo": (-7.8848, 112.4773),
            "Kampus UMM": (-7.9182, 112.5970)
        }
        
        # Temukan node OSM terdekat untuk setiap lokasi penting
        location_nodes = {}
        for name, coords in important_locations.items():
            # Format yang benar: X=longitude, Y=latitude
            nearest_node = ox.distance.nearest_nodes(G, X=coords[1], Y=coords[0])
            location_nodes[name] = nearest_node
        
        # Buat graph khusus dengan bobot jarak
        graph_dict = {}
        for name, node_id in location_nodes.items():
            graph_dict[name] = []
            
            # Cari jalur ke semua lokasi lain
            for other_name, other_node_id in location_nodes.items():
                if name != other_name:
                    try:
                        # Cari rute terpendek antara dua node
                        route = nx.shortest_path(G_undirected, node_id, other_node_id, weight='length')
                        
                        # Hitung total jarak rute
                        distance = sum(G_undirected[u][v]['length'] for u, v in zip(route[:-1], route[1:]))
                        
                        # Tambahkan ke graph
                        graph_dict[name].append((other_name, distance))
                    except nx.NetworkXNoPath:
                        # Jika tidak ada jalur, abaikan
                        console.print(f"[yellow]Tidak ada jalur dari {name} ke {other_name}[/yellow]")
                        pass
                    except Exception as e:
                        console.print(f"[yellow]Error mencari jalur dari {name} ke {other_name}: {str(e)}[/yellow]")
                        pass
        
        console.print("[green]Data OSM berhasil dimuat dari internet![/green]")
        return G, graph_dict, location_nodes
    
    except Exception as e:
        console.print(f"[bold red]Error saat memuat data OSM: {str(e)}[/bold red]")
        # Jika gagal memuat data, gunakan data statis untuk demonstrasi
        return None, get_static_data(), None
    
def get_static_data():
    """
    Data statis sebagai fallback jika tidak bisa memuat dari OSM
    """
    # Representasi graph lokasi-lokasi di Malang Raya
    # Format: {lokasi: [(tetangga1, jarak1), (tetangga2, jarak2), ...]}
    malang_raya = {
        "Alun-Alun Malang": [
            ("Stasiun Malang", 800), 
            ("Mall Olympic Garden", 600), 
            ("Balai Kota Malang", 500),
            ("Pasar Besar Malang", 400)
        ],
        "Stasiun Malang": [
            ("Alun-Alun Malang", 800), 
            ("Tugu Malang", 500), 
            ("Kampung Wisata Jodipan", 900)
        ],
        "Mall Olympic Garden": [
            ("Alun-Alun Malang", 600), 
            ("RS Saiful Anwar", 1200), 
            ("Balai Kota Malang", 700)
        ],
        "Universitas Brawijaya": [
            ("Universitas Negeri Malang", 1500), 
            ("Tugu Malang", 2500), 
            ("Balai Kota Malang", 3000)
        ],
        "Universitas Negeri Malang": [
            ("Universitas Brawijaya", 1500), 
            ("RS Saiful Anwar", 2000)
        ],
        "RS Saiful Anwar": [
            ("Mall Olympic Garden", 1200), 
            ("Universitas Negeri Malang", 2000), 
            ("Kampung Wisata Jodipan", 1800)
        ],
        "Balai Kota Malang": [
            ("Alun-Alun Malang", 500), 
            ("Mall Olympic Garden", 700), 
            ("Tugu Malang", 800), 
            ("Universitas Brawijaya", 3000)
        ],
        "Terminal Arjosari": [
            ("Tugu Malang", 4500), 
            ("Kampus UMM", 5000), 
            ("Taman Rekreasi Sengkaling", 6000)
        ],
        "Stadion Kanjuruhan": [
            ("Pasar Besar Malang", 7000), 
            ("Alun-Alun Malang", 7500)
        ],
        "Jatim Park 1": [
            ("Jatim Park 2", 500), 
            ("Museum Angkut", 1500), 
            ("Alun-Alun Batu", 2000)
        ],
        "Jatim Park 2": [
            ("Jatim Park 1", 500), 
            ("Museum Angkut", 1200), 
            ("Selecta", 6000)
        ],
        "Museum Angkut": [
            ("Jatim Park 1", 1500), 
            ("Jatim Park 2", 1200), 
            ("Alun-Alun Batu", 1500), 
            ("Selecta", 5500)
        ],
        "Alun-Alun Batu": [
            ("Jatim Park 1", 2000), 
            ("Museum Angkut", 1500), 
            ("Selecta", 5000), 
            ("Coban Rondo", 7000)
        ],
        "Selecta": [
            ("Jatim Park 2", 6000), 
            ("Museum Angkut", 5500), 
            ("Alun-Alun Batu", 5000), 
            ("Coban Rondo", 8000)
        ],
        "Kampung Wisata Jodipan": [
            ("Stasiun Malang", 900), 
            ("RS Saiful Anwar", 1800), 
            ("Pasar Besar Malang", 800)
        ],
        "Taman Rekreasi Sengkaling": [
            ("Terminal Arjosari", 6000), 
            ("Kampus UMM", 1200)
        ],
        "Pasar Besar Malang": [
            ("Alun-Alun Malang", 400), 
            ("Kampung Wisata Jodipan", 800), 
            ("Stadion Kanjuruhan", 7000)
        ],
        "Tugu Malang": [
            ("Stasiun Malang", 500), 
            ("Balai Kota Malang", 800), 
            ("Terminal Arjosari", 4500), 
            ("Universitas Brawijaya", 2500)
        ],
        "Coban Rondo": [
            ("Alun-Alun Batu", 7000), 
            ("Selecta", 8000)
        ],
        "Kampus UMM": [
            ("Terminal Arjosari", 5000), 
            ("Taman Rekreasi Sengkaling", 1200)
        ]
    }
    
    console.print("[yellow]Menggunakan data statis untuk demonstrasi.[/yellow]")
    return malang_raya

def visualize_route(G, location_nodes, route):
    """
    Visualisasi rute pada peta menggunakan folium dengan nama file yang unik
    """
    try:
        if G is None or location_nodes is None:
            console.print("[red]Tidak dapat memvisualisasikan rute: data OSM tidak tersedia[/red]")
            return
        
        # Buat nama file unik berdasarkan waktu dan lokasi
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        start_location = route[0].replace(" ", "_")
        end_location = route[-1].replace(" ", "_")
        
        # Dapatkan koordinat untuk setiap lokasi dalam rute
        route_nodes = [location_nodes[loc] for loc in route]
        
        # Buat route sebagai list node pairs
        pairs = []
        for i in range(len(route_nodes)-1):
            pairs.append((route_nodes[i], route_nodes[i+1]))
            
        # Inisialisasi peta
        map_center = [G.nodes[route_nodes[0]]['y'], G.nodes[route_nodes[0]]['x']]
        route_map = folium.Map(location=map_center, zoom_start=13)
        
        # Plot edges
        for u, v in pairs:
            try:
                # Find the shortest path between points
                path = nx.shortest_path(G, u, v, weight='length')
                
                # Extract coordinates for the path
                path_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in path]
                
                # Add path to map
                folium.PolyLine(
                    path_coords, 
                    color='red',
                    weight=4,
                    opacity=0.8
                ).add_to(route_map)
                
            except Exception as e:
                console.print(f"[yellow]Error plotting segment: {str(e)}[/yellow]")
        
        # Add markers for each location
        for i, node in enumerate(route_nodes):
            try:
                lat = G.nodes[node]['y']
                lon = G.nodes[node]['x']
                
                # Choose icon based on position
                if i == 0:  # Start
                    icon = folium.Icon(color='green', icon='play')
                    popup_text = f"Start: {route[i]}"
                elif i == len(route_nodes) - 1:  # End
                    icon = folium.Icon(color='red', icon='stop')
                    popup_text = f"End: {route[i]}"
                else:  # Waypoint
                    icon = folium.Icon(color='blue', icon='flag')
                    popup_text = f"Waypoint {i}: {route[i]}"
                
                folium.Marker(
                    [lat, lon],
                    popup=popup_text,
                    icon=icon
                ).add_to(route_map)
                
            except Exception as e:
                console.print(f"[yellow]Error adding marker for {route[i]}: {str(e)}[/yellow]")
        
        # Buat direktori untuk menyimpan hasil peta jika belum ada
        maps_dir = "route_maps"
        if not os.path.exists(maps_dir):
            os.makedirs(maps_dir)
        
        # Simpan ke file HTML dengan nama unik
        map_filename = f"{maps_dir}/route_{start_location}_to_{end_location}_{timestamp}.html"
        route_map.save(map_filename)
        console.print(f"[green]Peta rute telah disimpan ke [bold]{map_filename}[/bold][/green]")
        console.print("[yellow]Silakan buka file tersebut di browser Anda.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error saat membuat visualisasi: {str(e)}[/red]")

def visualize_graph_networkx(graph):
    """
    Visualisasi graph menggunakan NetworkX
    """
    try:
        G = nx.Graph()
        
        # Tambahkan node dan edge ke graph
        for source, destinations in graph.items():
            for dest, weight in destinations:
                G.add_edge(source, dest, weight=weight)
        
        # Atur layout
        pos = nx.spring_layout(G, seed=42)
        
        plt.figure(figsize=(12, 10))
        plt.title("Graf Lokasi di Malang Raya")
        
        # Gambar node dan edge
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
        nx.draw_networkx_edges(G, pos, width=1, alpha=0.7)
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        # Tambahkan label bobot pada edge
        edge_labels = {(u, v): f"{d['weight']:.0f}m" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
        
        plt.axis('off')
        plt.tight_layout()
        
        # Simpan dan tampilkan
        plt.savefig('malang_graph.png', dpi=300, bbox_inches='tight')
        console.print("[green]Graf telah disimpan ke [bold]malang_graph.png[/bold][/green]")
        plt.close()
    
    except Exception as e:
        console.print(f"[red]Error saat membuat visualisasi graf: {str(e)}[/red]")

def tampilkan_hasil(start, goals, hasil, waktu_komputasi, is_multi=False):
    """Menampilkan hasil pencarian rute"""
    if hasil:
        path, cost, visited_nodes = hasil
        
        table = Table(title=f"Hasil Pencarian Rute dengan UCS")
        table.add_column("Informasi", style="cyan")
        table.add_column("Detail", style="green")
        
        table.add_row("Dari", start)
        
        if is_multi:
            table.add_row("Ke (Multi-Goal)", ", ".join(goals))
        else:
            table.add_row("Ke", goals)
            
        table.add_row("Rute", " -> ".join(path))
        table.add_row("Total jarak", f"{cost:.2f} meter")
        table.add_row("Estimasi waktu", f"{cost/833.33:.2f} menit")  # Asumsi kecepatan 50 km/jam
        table.add_row("Node dikunjungi", str(len(visited_nodes)))
        table.add_row("Waktu komputasi", f"{waktu_komputasi:.4f} detik")
        
        console.print(table)
        return path
    else:
        if is_multi:
            console.print(Panel(f"[bold red]Tidak ada rute yang ditemukan dari {start} ke salah satu tujuan.[/bold red]"))
        else:
            console.print(Panel(f"[bold red]Tidak ada rute yang ditemukan dari {start} ke {goals}.[/bold red]"))
        return None

def show_banner():
    print(f"OSMnx version: {ox.__version__}")
    """Menampilkan banner aplikasi"""
    f = Figlet(font='slant')
    banner = f.renderText('UCS Routing')
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print(Panel("[bold yellow]SISTEM PENCARIAN RUTE PENGIRIMAN BARANG DI MALANG RAYA[/bold yellow]\n"
                      "[green]Menggunakan Algoritma Uniform Cost Search (UCS)[/green]\n"
                      "[blue]UTS Kecerdasan Artificial - 2025[/blue]"))

def main():
    """Fungsi utama untuk menjalankan aplikasi"""
    show_banner()
    
    # Muat data OSM
    G, malang_graph, location_nodes = load_malang_osm_data()
    
    # Definisikan waktu maksimal operasional kendaraan (dalam menit)
    max_operating_time = 120  # 2 jam
    
    while True:
        # Tampilkan menu utama
        choice = questionary.select(
            "Pilih Menu:",
            choices=[
                "1. Cari Rute Pengiriman",
                "2. Lihat Graf Lokasi",
                "3. Keluar"
            ]).ask()
        
        if choice == "1. Cari Rute Pengiriman":
            # Tampilkan daftar lokasi
            daftar_lokasi = sorted(malang_graph.keys())
            
            # Pilih lokasi awal
            console.print("\n[bold cyan]Pilih Lokasi Awal dan Tujuan[/bold cyan]")
            
            lokasi_awal = questionary.select(
                "Pilih lokasi awal:",
                choices=daftar_lokasi
            ).ask()
            
            # Tanya apakah ini pencarian multi-tujuan
            is_multi = questionary.confirm("Apakah Anda ingin melakukan pengiriman ke beberapa tujuan (multi-goal)?").ask()
            
            if is_multi:
                # Multi-goal: pilih beberapa tujuan
                lokasi_tujuan = []
                jumlah_tujuan = questionary.text(
                    "Berapa jumlah tujuan yang ingin dikunjungi?",
                    validate=lambda text: text.isdigit() and 1 <= int(text) <= 5,
                    instruction="(Masukkan angka 1-5)"
                ).ask()
                jumlah_tujuan = int(jumlah_tujuan)
                
                for i in range(jumlah_tujuan):
                    # Filter lokasi yang sudah dipilih
                    available_locations = [loc for loc in daftar_lokasi if loc != lokasi_awal and loc not in lokasi_tujuan]
                    if not available_locations:
                        console.print("[bold red]Semua lokasi sudah dipilih![/bold red]")
                        break
                        
                    next_destination = questionary.select(
                        f"Pilih tujuan ke-{i+1}:",
                        choices=available_locations
                    ).ask()
                    lokasi_tujuan.append(next_destination)
                
                console.print(f"[green]Tujuan yang akan dikunjungi: {', '.join(lokasi_tujuan)}[/green]")
            else:
                # Single-goal: pilih satu tujuan
                lokasi_tujuan = questionary.select(
                    "Pilih lokasi tujuan:",
                    choices=[loc for loc in daftar_lokasi if loc != lokasi_awal]
                ).ask()
                
                # Memastikan lokasi awal dan tujuan berbeda
                if lokasi_awal == lokasi_tujuan:
                    console.print("[bold red]Lokasi awal dan tujuan sama. Silakan pilih lokasi yang berbeda.[/bold red]")
                    continue
            
            # Tanya pengguna apakah ingin melihat ilustrasi proses
            tampilkan_proses = questionary.confirm("Apakah Anda ingin melihat ilustrasi proses pencarian?").ask()
            
            # Inisialisasi algoritma UCS
            ucs = UniformCostSearch(malang_graph)
            
            # Lakukan pencarian dan hitung waktu
            start_time = time.time()
            
            if is_multi:
                hasil = ucs.search_multigoal(lokasi_awal, lokasi_tujuan, tampilkan_proses)
            else:
                hasil = ucs.search(lokasi_awal, lokasi_tujuan, tampilkan_proses)
                
            end_time = time.time()
            waktu_komputasi = end_time - start_time
            
            # Tampilkan hasil
            route = tampilkan_hasil(lokasi_awal, lokasi_tujuan, hasil, waktu_komputasi, is_multi)
            
            # Cek batas waktu operasional
            if hasil:
                path, cost, _ = hasil
                estimated_time = cost / 833.33  # Asumsi kecepatan 50 km/jam (833.33 m/menit)
                
                if estimated_time > max_operating_time:
                    console.print(f"[bold red]Peringatan: Rute ini membutuhkan waktu {estimated_time:.2f} menit, "
                                f"melebihi batas waktu operasional {max_operating_time} menit![/bold red]")
            
            # Tanya pengguna apakah ingin melihat rute pada peta
            if route and G is not None and location_nodes is not None:
                if questionary.confirm("Apakah Anda ingin melihat visualisasi rute pada peta?").ask():
                    visualize_route(G, location_nodes, route)
        
        elif choice == "2. Lihat Graf Lokasi":
            console.print("\n[bold cyan]Visualisasi Graf Lokasi[/bold cyan]")
            visualize_graph_networkx(malang_graph)
        
        elif choice == "3. Keluar":
            console.print("[bold green]Terima kasih telah menggunakan aplikasi ini![/bold green]")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Program dihentikan oleh pengguna.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]Terjadi kesalahan: {str(e)}[/bold red]")