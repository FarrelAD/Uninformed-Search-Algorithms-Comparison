import json
import networkx as nx
import os
import osmnx as ox
from pathlib import Path
import pickle
from rich.console import Console

from config.config import DATA_DIR
from store.states import GlobalState

console = Console()

def save_osm_data(G: nx.MultiDiGraph) -> None:
    """
    Save OpenStreetMap (OSM) data to a local file using pickle
    """
    try:
        if not Path(DATA_DIR).exists():
            os.makedirs(DATA_DIR)
        
        filepath = Path(DATA_DIR) / "malang_osm_data.pkl"
        
        with open(filepath, 'wb') as f:
            pickle.dump(G, f)
        
        console.print(f"[green]Data OSM berhasil disimpan ke [bold]{filepath}[/bold][/green]")
    except Exception as e:
        console.print(f"[red]Error saat menyimpan data OSM: {str(e)}[/red]")

def get_location_coordinates(G: nx.MultiDiGraph, locations: list) -> dict | None:
    """
    Get the coordinates of a location using OSM Nominatim API
    """
    try:
        location_coordinates = []
        for loc in locations:
            geolocator = ox.geocoder.geocode(loc)
            if geolocator:
                node_id = ox.distance.nearest_nodes(G, X=geolocator[1], Y=geolocator[0])
                location_coordinates.append({
                    "name": loc,
                    "latitude": geolocator[0],
                    "longitude": geolocator[1],
                    "node_id": node_id,
                })
            else:
                location_coordinates.append({
                    "name": loc,
                    "latitude": None,
                    "longitude": None,
                    "node_id": None,
                })
        return location_coordinates
    except Exception as e:
        console.print(f"[red]Error occurred while getting location coordinates: {str(e)}[/red]")
        return None

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
        with open(Path(DATA_DIR) / "malang_locations.json", 'r') as f:
            malang_locations = json.load(f)
        
        with open(Path(DATA_DIR) / "malang_graph.json", 'r') as f:
            malang_graph = json.load(f)
        
        # Buat graph khusus dengan bobot jarak
        G_undirected = nx.Graph(G)
        new_graph = []
        for index, loc in enumerate(malang_locations):
            new_graph.append({
                "node": loc["name"],
                "branch": []
            })

            branch = next((node["branch"] for node in malang_graph if node["node"] == loc["name"]), None)
            
            if not branch:
                continue
            
            for node in branch:
                try:
                    branch_node_id = next((n["node_id"] for n in malang_locations if n["name"] == node["node"]), None)
                    route = nx.shortest_path(G_undirected, loc["node_id"], branch_node_id, weight='length')
                    distance = sum(G_undirected[u][v]['length'] for u, v in zip(route[:-1], route[1:]))
                    new_graph[index]["branch"].append({
                        "node": node["node"], 
                        "distance": distance
                    })
                except nx.NetworkXNoPath:
                    console.print(f"[yellow]Tidak ada jalur dari {loc["name"]} ke {node["node"]}[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]Error mencari jalur dari {loc["name"]} ke {node["node"]}: {str(e)}[/yellow]")
        
        with open(Path(DATA_DIR) / "malang_graph.json", 'w') as f:
            json.dump(new_graph, f, indent=4)
        
        GlobalState.G = G
        GlobalState.malang_graph = new_graph
        GlobalState.location_nodes = malang_locations
    except Exception as e:
        console.print(f"[yellow]Error saat memproses data OSM dari cache: {str(e)}. Mencoba memuat ulang dari OSM...[/yellow]")

def load_osm_data_online() -> nx.MultiDiGraph | None:
    try:
        console.print("[yellow]Load OSM data from the internet...[/yellow]")
        
        G = ox.graph_from_place("Malang, East Java, Indonesia", network_type="drive", simplify=True)
        
        locations = [
            "Alun-Alun Malang, Malang, Indonesia",
            "Stasiun Malang Kota Baru, Malang, Indonesia",
            "Mall Olympic Garden, Malang, Indonesia",
            "Universitas Brawijaya, Malang, Indonesia",
            "Universitas Negeri Malang, Malang, Indonesia",
            "RSUD Saiful Anwar, Malang, Indonesia",
            "Balai Kota Malang, Malang, Indonesia",
            "Terminal Arjosari, Malang, Indonesia",
            "Stadion Kanjuruhan, Malang, Indonesia",
            "Jawa Timur Park 1, Batu, Indonesia",
            "Jawa Timur Park 2, Batu, Indonesia",
            "Museum Angkut, Batu, Indonesia",
            "Alun-Alun Batu, Batu, Indonesia",
            "Taman Rekreasi Selecta, Batu, Indonesia",
            "Kampung Warna-Warni Jodipan, Malang, Indonesia",
            "Taman Rekreasi Sengkaling, Malang, Indonesia",
            "Pasar Besar Malang, Malang, Indonesia",
            "Paralayang, Batu, Indonesia",
            "Coban Rondo, Batu, Indonesia",
            "Kampus UMM, Malang, Indonesia"
        ]
        
        locations_coordinate = get_location_coordinates(G, locations)
        
        with open(Path(DATA_DIR) / "malang_locations.json", 'w') as f:
            json.dump(locations_coordinate, f, indent=4)

        if not 'length' in list(G.edges(data=True))[0][2]:
            G = ox.add_edge_lengths(G)
        
        save_osm_data(G)
        
        console.print("[green]OSM data loaded successfully from the internet![/green]")
        return G
    except Exception as e:
        console.print(f"[bold red]Error occurred while loading OSM data from the internet: {str(e)}[/bold red]")
        return None
