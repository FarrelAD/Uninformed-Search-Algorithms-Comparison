import datetime
import folium
import networkx as nx
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.config import MAPS_DIR

console = Console()

def visualize_route(G: nx.multidigraph, location_nodes: dict, route: list) -> None:
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
        
        if not os.path.exists(MAPS_DIR):
            os.makedirs(MAPS_DIR)
        
        map_filename = f"{MAPS_DIR}/route_{start_location}_to_{end_location}_{timestamp}.html"
        route_map.save(map_filename)
        console.print(f"[green]Peta rute telah disimpan ke [bold]{map_filename}[/bold][/green]")
        console.print("[yellow]Silakan buka file tersebut di browser Anda.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error saat membuat visualisasi: {str(e)}[/red]")

def show_result(start: str, goals: str, result: tuple[list, int, list], time_computation: float, is_multi: bool = False) -> None | list:
    """Menampilkan hasil pencarian rute"""
    if not result:
        if is_multi:
            console.print(Panel(f"[bold red]Tidak ada rute yang ditemukan dari {start} ke salah satu tujuan.[/bold red]"))
        else:
            console.print(Panel(f"[bold red]Tidak ada rute yang ditemukan dari {start} ke {goals}.[/bold red]"))
        return None
    
    path, cost, visited_nodes = result
    
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
    table.add_row("Waktu komputasi", f"{time_computation:.4f} detik")
    
    console.print(table)
    return path
