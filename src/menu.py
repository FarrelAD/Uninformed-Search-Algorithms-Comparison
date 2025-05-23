import json
import matplotlib.pyplot as plt
import networkx as nx
import os
from pathlib import Path
from rich.console import Console
import questionary

from algorithms.bfs import run_bfs
from algorithms.dfs import run_dfs
from algorithms.ucs import run_ucs
from algorithms.dls import run_dls
from config.config import IMG_DIR, DATA_DIR
from helpers.system_helper import open_image
from store.states import GlobalState

console = Console()

def find_route_destination() -> None:
    list_of_locations = sorted([node["name"] for node in GlobalState.location_nodes])

    console.print("\n[bold cyan]Select start and destination location[/bold cyan]")
    
    GlobalState.start_location = questionary.select(
        "Select start location:",
        choices=list_of_locations
    ).ask()
    
    GlobalState.is_multi = questionary.confirm("Do you want to send to multiple destinations? (multi-goal)?").ask()
    
    if GlobalState.is_multi:
        destination_location = []
        total_destionation = questionary.text(
            "How many destination do you want to visit?",
            validate=lambda text: text.isdigit() and 1 <= int(text) <= (len(list_of_locations) - 1),
            instruction=f"Enter the number of destination (1-{len(list_of_locations) - 1}): "
        ).ask()
        total_destionation = int(total_destionation)
        
        for i in range(total_destionation):
            available_locations = [loc for loc in list_of_locations if loc != GlobalState.start_location and loc not in destination_location]
            if not available_locations:
                console.print("[bold red]All locations have been selected![/bold red]")
                break
            
            next_destination = questionary.select(
                f"Select destination {i+1}:",
                choices=available_locations
            ).ask()
            destination_location.append(next_destination)
        
        console.print(f"[green]Destinations to visit: \n{''.join(f" - {d}\n" for d in destination_location)}[/green]")
    else:
        destination_location = questionary.select(
            "Select destination:",
            choices=[loc for loc in list_of_locations if loc != GlobalState.start_location]
        ).ask()
    
    # Set global state for destination locations
    GlobalState.destination_location = destination_location

    max_operating_time = questionary.text(
        "What's the maximum vehicle operation time (in minutes)?",
        validate=lambda text: text.isdigit() and int(text) > 0,
        default="120",
        instruction="(default: 120 minutes)"
    ).ask()
    GlobalState.max_operating_time = int(max_operating_time)
    
    avg_speed = questionary.text(
        "What is the average speed (km/h)?",
        validate=lambda x: (
            True if x.replace('.', '', 1).isdigit() else "Please enter a valid number"
        )
    ).ask()
    
    GlobalState.avg_speed = float(avg_speed) * 1000 / 60
    
    algorithm_choice = questionary.select(
        "Select searching algorithm:",
        choices=[
            "1. Breadth-First Search (BFS)",
            "2. Depth-First Search (DFS)",
            "3. Uniform Cost Search (UCS)",
            "4. Depth-Limited Search (DLS)"
        ]
    ).ask()
    
    GlobalState.show_process = questionary.confirm("Do you want to see the illustration of the search process?").ask()
    
    if algorithm_choice == "1. Breadth-First Search (BFS)":
        run_bfs()
    elif algorithm_choice == "2. Depth-First Search (DFS)":
        run_dfs()
    elif algorithm_choice == "3. Uniform Cost Search (UCS)":
        run_ucs()
    elif algorithm_choice == "4. Depth-Limited Search (DLS)":
        run_dls()

def visualize_graph_networkx() -> None:
    """
    Visualization of the graph using NetworkX and Matplotlib. Saves the graph as an image file.
    """
    
    console.print("\n[bold cyan]Visualization of Location Graph[/bold cyan]")
    
    try:
        if not Path(IMG_DIR).exists():
            os.makedirs(DATA_DIR)
        
        G = nx.Graph()
        
        with open(Path(DATA_DIR, "malang_locations.json"), "r") as f:
            locations = json.load(f)
            
        for i in range(len(locations)):
            loc = locations[i]
            G.add_node(loc['name'], pos=(loc['longitude'], loc['latitude']))
        
        with open(Path(DATA_DIR) / "malang_graph.json", "r") as f:
            malang_graph = json.load(f)
        
        for loc in malang_graph:
            branch = next((node["branch"] for node in malang_graph if node["node"] == loc["node"]), None)
            
            if not branch:
                continue
            
            for node in branch:
                G.add_edge(loc["node"], node["node"], distance=node["distance"])

        plt.figure(figsize=(20, 20))
        pos = nx.get_node_attributes(G, 'pos')
        nx.draw(
            G, pos, 
            with_labels=True,
            node_size=1200, 
            node_color='skyblue', 
            font_size=9, 
            edge_color='orange', 
            width=2
        )
        
        edge_labels = {(u, v): f"{d['distance']:.0f}m" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

        plt.title("Graph Visualization of Malang Locations", fontsize=16)
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True)
        
        filename = Path(IMG_DIR) / "malang_graph.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        console.print("[green]Graph has been saved to [bold]malang_graph.png[/bold][/green]")
        open_image(filename)
    except Exception as e:
        console.print(f"[red]Error occurred while creating graph visualization: {str(e)}[/red]")
