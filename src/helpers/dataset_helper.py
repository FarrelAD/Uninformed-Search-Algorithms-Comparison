import json
import networkx as nx
import os
import osmnx as ox
import pickle
from rich.console import Console

from config.config import DATA_DIR
from store.states import GlobalState

console = Console()

def save_osm_data(G: nx.MultiDiGraph, filename="malang_osm_data.pkl") -> None:
    """
    Save OpenStreetMap (OSM) data to a local file using pickle
    """
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'wb') as f:
            pickle.dump(G, f)
        
        console.print(f"[green]Data OSM berhasil disimpan ke [bold]{filepath}[/bold][/green]")
    except Exception as e:
        console.print(f"[red]Error saat menyimpan data OSM: {str(e)}[/red]")

def load_osm_data_from_file(filename="malang_osm_data.pkl") -> nx.MultiDiGraph | None:
    """
    Load OpenStreetMap (OSM) data from a local file using pickle
    """
    try:
        filepath = os.path.join(DATA_DIR, filename)
        
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

def load_malang_osm_data() -> None:
    """
    Loads OSM data for Malang Raya region.
    Attempts to load from cache first, if not available then fetch from OSM.
    """
    G = load_osm_data_from_file()
    
    if G is None:
        G = load_osm_data_online()

    try:
        with open(os.path.join(DATA_DIR, "malang_locations.json"), 'r') as f:
            important_locations = json.load(f)
        
        # Temukan node OSM terdekat untuk setiap lokasi penting
        location_nodes = {}
        for name, coords in important_locations.items():
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
                        route = nx.shortest_path(G_undirected, node_id, other_node_id, weight='length')
                        
                        distance = sum(G_undirected[u][v]['length'] for u, v in zip(route[:-1], route[1:]))
                        
                        graph_dict[name].append((other_name, distance))
                    except nx.NetworkXNoPath:
                        console.print(f"[yellow]Tidak ada jalur dari {name} ke {other_name}[/yellow]")
                        pass
                    except Exception as e:
                        console.print(f"[yellow]Error mencari jalur dari {name} ke {other_name}: {str(e)}[/yellow]")
                        pass
        
        console.print("[green]Data OSM berhasil dimuat dari cache lokal![/green]")
        
        GlobalState.G = G
        GlobalState.malang_graph = graph_dict
        GlobalState.location_nodes = location_nodes
    except Exception as e:
        console.print(f"[yellow]Error saat memproses data OSM dari cache: {str(e)}. Mencoba memuat ulang dari OSM...[/yellow]")

def load_osm_data_online() -> nx.MultiDiGraph | None:
    try:
        console.print("[yellow]Memuat data OSM untuk Malang Raya dari internet...[/yellow]")
        
        G = ox.graph_from_place("Malang, East Java, Indonesia", network_type="drive", simplify=True)
        
        if not 'length' in list(G.edges(data=True))[0][2]:
            G = ox.add_edge_lengths(G)
        
        save_osm_data(G)
        
        console.print("[green]Data OSM berhasil dimuat dari internet![/green]")
        return G
    except Exception as e:
        console.print(f"[bold red]Error saat memuat data OSM: {str(e)}[/bold red]")
        return None
    
def get_static_data() -> dict:
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
