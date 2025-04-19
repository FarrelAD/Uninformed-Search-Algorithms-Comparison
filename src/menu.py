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
from helpers.system_helper import open_image
from store.states import GlobalState

console = Console()

def find_route_destination() -> None:
    list_of_locations = sorted(GlobalState.malang_graph.keys())

    console.print("\n[bold cyan]Select start and destination location[/bold cyan]")
    
    GlobalState.start_location = questionary.select(
        "Pilih lokasi awal:",
        choices=list_of_locations
    ).ask()
    
    is_multi = questionary.confirm("Do you want to send to multiple destinations? (multi-goal)?").ask()
    
    if is_multi:
        destination_location = []
        total_destionation = questionary.text(
            "How many destination do you want to visit?",
            validate=lambda text: text.isdigit() and 1 <= int(text) <= 5,
            instruction="Enter the number of destination (1-5): "
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
        
        console.print(f"[green]Destinations to visit: {', '.join(destination_location)}[/green]")
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
    
    algorithm_choice = questionary.select(
        "Select searching algorithm:",
        choices=[
            "1. Breadth-First Search (BFS)",
            "2. Depth-First Search (DFS)",
            "3. Uniform Cost Search (UCS)",
            "4. Depth-Limited Search (DLS)"
        ]
    ).ask()
    
    show_process = questionary.confirm("Do you want to see the illustration of the search process?").ask()
    
    if algorithm_choice == "1. Breadth-First Search (BFS)":
        run_bfs()
    elif algorithm_choice == "2. Depth-First Search (DFS)":
        run_dfs()
    elif algorithm_choice == "3. Uniform Cost Search (UCS)":
        run_ucs()
    elif algorithm_choice == "4. Depth-Limited Search (DLS)":
        run_dls()

def visualize_graph_networkx(graph: dict) -> None:
    """
    Visualization of the graph using NetworkX and Matplotlib. Saves the graph as an image file.
    Args:
        graph (dict): The graph data structure with locations and their connections.
    """
    
    console.print("\n[bold cyan]Visualization of Location Graph[/bold cyan]")
    
    try:
        G = nx.Graph()
        
        for source, destinations in graph.items():
            for dest, weight in destinations:
                G.add_edge(source, dest, weight=weight)
        
        pos = nx.spring_layout(G, seed=42)
        
        plt.figure(figsize=(12, 10))
        plt.title("Graph Data Structure of Malang Raya Locations")
        
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
        nx.draw_networkx_edges(G, pos, width=1, alpha=0.7)
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        edge_labels = {(u, v): f"{d['weight']:.0f}m" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
        
        plt.axis('off')
        plt.tight_layout()
        
        if not os.path.exists(IMG_DIR):
            os.makedirs(IMG_DIR)
        
        filename = os.path.join(IMG_DIR, "malang_graph.png")
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        console.print("[green]Graph has been saved to [bold]malang_graph.png[/bold][/green]")
        plt.close()
        
        open_image(filename)
    except Exception as e:
        console.print(f"[red]Error occurred while creating graph visualization: {str(e)}[/red]")
