import matplotlib.pyplot as plt
import networkx as nx
import os
from rich.console import Console
import questionary

from bfs.bfs import run_bfs
from dfs.dfs import run_dfs
from ucs.ucs import run_ucs
from dls.dls import run_dls
from config.config import IMG_DIR


console = Console()

def find_route_destination(G: nx.MultiDiGraph, malang_graph: dict, location_nodes: dict) -> None:
    daftar_lokasi = sorted(malang_graph.keys())

    console.print("\n[bold cyan]Pilih Lokasi Awal dan Tujuan[/bold cyan]")
    
    lokasi_awal = questionary.select(
        "Pilih lokasi awal:",
        choices=daftar_lokasi
    ).ask()
    
    is_multi = questionary.confirm("Apakah Anda ingin melakukan pengiriman ke beberapa tujuan (multi-goal)?").ask()
    
    if is_multi:
        lokasi_tujuan = []
        jumlah_tujuan = questionary.text(
            "Berapa jumlah tujuan yang ingin dikunjungi?",
            validate=lambda text: text.isdigit() and 1 <= int(text) <= 5,
            instruction="(Masukukan angka 1-5)"
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
        lokasi_tujuan = questionary.select(
            "Pilih lokasi tujuan:",
            choices=[loc for loc in daftar_lokasi if loc != lokasi_awal]
        ).ask()
        
        if lokasi_awal == lokasi_tujuan:
            console.print("[bold red]Lokasi awal dan tujuan sama. Silakan pilih lokasi yang berbeda.[/bold red]")
    
    max_operating_time = int(questionary.text(
        "Berapa waktu maksimal operasional kendaraan (dalam menit)?",
        validate=lambda text: text.isdigit() and int(text) > 0,
        default="120",
        instruction="(default: 120 menit)"
    ).ask())
    
    algorithm_choice = questionary.select(
        "Pilih algoritma pencarian:",
        choices=[
            "1. Breadth-First Search (BFS)",
            "2. Depth-First Search (DFS)",
            "3. Uniform Cost Search (UCS)",
            "5. Depth-Limited Search (DLS)"
        ]
    ).ask()
    
    tampilkan_proses = questionary.confirm("Apakah Anda ingin melihat ilustrasi proses pencarian?").ask()
    
    if algorithm_choice == "1. Breadth-First Search (BFS)":
        run_bfs()
    elif algorithm_choice == "2. Depth-First Search (DFS)":
        run_dfs()
    elif algorithm_choice == "3. Uniform Cost Search (UCS)":
        run_ucs(G, malang_graph, location_nodes, lokasi_awal, lokasi_tujuan, is_multi, tampilkan_proses, max_operating_time)
    elif algorithm_choice == "4. Depth-Limited Search":
        run_dls()

def visualize_graph_networkx(graph: dict) -> None:
    """
    Visualisasi graph menggunakan NetworkX. Disimpan dalam format PNG.
    """
    
    console.print("\n[bold cyan]Visualisasi Graf Lokasi[/bold cyan]")
    
    try:
        G = nx.Graph()
        
        for source, destinations in graph.items():
            for dest, weight in destinations:
                G.add_edge(source, dest, weight=weight)
        
        pos = nx.spring_layout(G, seed=42)
        
        plt.figure(figsize=(12, 10))
        plt.title("Graf Lokasi di Malang Raya")
        
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
        nx.draw_networkx_edges(G, pos, width=1, alpha=0.7)
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        edge_labels = {(u, v): f"{d['weight']:.0f}m" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
        
        plt.axis('off')
        plt.tight_layout()
        
        if not os.path.exists(IMG_DIR):
            os.makedirs(IMG_DIR)
            
        plt.savefig(f"{IMG_DIR}/malang_graph.png", dpi=300, bbox_inches='tight')
        console.print("[green]Graf telah disimpan ke [bold]malang_graph.png[/bold][/green]")
        plt.close()
    
    except Exception as e:
        console.print(f"[red]Error saat membuat visualisasi graf: {str(e)}[/red]")