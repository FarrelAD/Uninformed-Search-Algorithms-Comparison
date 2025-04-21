import datetime
import folium
import networkx as nx
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import webbrowser

from config.config import MAPS_DIR, JINJA_ENV
from store.states import GlobalState

console = Console()

def visualize_route(route: list) -> None:
    """
    Visualizes the route on a map using folium and saves it to a file with a unique name.
    """
    try:
        if GlobalState.G is None or GlobalState.location_nodes is None:
            console.print("[red]Tidak dapat memvisualisasikan rute: data OSM tidak tersedia[/red]")
            return
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        start_location = route[0].replace(" ", "_")
        end_location = route[-1].replace(" ", "_")
        
        # Create a dictionary for quick lookup of node_ids by location name
        location_dict = {loc["name"]: loc["node_id"] for loc in GlobalState.location_nodes}
        
        # Get node IDs for each location in the route
        route_nodes = []
        for loc in route:
            if loc in location_dict:
                route_nodes.append(location_dict[loc])
            else:
                console.print(f"[yellow]Warning: Location '{loc}' not found in location_nodes[/yellow]")
        
        if not route_nodes:
            console.print("[red]No valid nodes found for visualization[/red]")
            return
            
        pairs = []
        for i in range(len(route_nodes)-1):
            pairs.append((route_nodes[i], route_nodes[i+1]))
            
        map_center = [GlobalState.G.nodes[route_nodes[0]]['y'], GlobalState.G.nodes[route_nodes[0]]['x']]
        route_map = folium.Map(location=map_center, zoom_start=13)
        
        for u, v in pairs:
            try:
                path = nx.shortest_path(GlobalState.G, u, v, weight='length')
                
                path_coords = [(GlobalState.G.nodes[node]['y'], GlobalState.G.nodes[node]['x']) for node in path]
                
                folium.PolyLine(
                    path_coords, 
                    color='red',
                    weight=4,
                    opacity=0.8
                ).add_to(route_map)
                
            except Exception as e:
                console.print(f"[yellow]Error plotting segment: {str(e)}[/yellow]")
        
        # Find corresponding location info for each node
        node_to_location = {}
        for loc in GlobalState.location_nodes:
            node_to_location[loc["node_id"]] = loc
        
        for i, node in enumerate(route_nodes):
            try:
                if node in node_to_location:
                    lat = node_to_location[node]["latitude"]
                    lon = node_to_location[node]["longitude"]
                else:
                    lat = GlobalState.G.nodes[node]['y']
                    lon = GlobalState.G.nodes[node]['x']
                
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
        
        map_filename = os.path.join(MAPS_DIR, f"route_{start_location}_to_{end_location}_{timestamp}.html")
        html_template = JINJA_ENV.get_template("map.html")
        output_html = html_template.render(map=route_map._repr_html_())
        
        with open(map_filename, "w") as f:
            f.write(output_html)
        
        console.print(f"[green]Peta rute telah disimpan ke [bold]{map_filename}[/bold][/green]")
        console.print("[yellow]Silakan buka file tersebut di browser Anda.[/yellow]")
        
        webbrowser.open(f"file://{map_filename}", new=2)
    except Exception as e:
        console.print(f"[red]Error saat membuat visualisasi: {str(e)}[/red]")

def show_result(method: str, result: tuple[list[str], float, int] | list[tuple[list[str], float, int]], time_computation: float) -> None:
    """
    Show the result of the search in a table format.
    """
    if not result:
        if GlobalState.is_multi:
            console.print(Panel(f"[bold red]Tidak ada rute yang ditemukan dari {GlobalState.start_location} ke salah satu tujuan.[/bold red]"))
        else:
            console.print(Panel(f"[bold red]Tidak ada rute yang ditemukan dari {GlobalState.start_location} ke {GlobalState.destination_location}.[/bold red]"))
        return
    
    
    table = Table(title=f"Results of Route Search with {method}")
    table.add_column("Info", style="cyan")
    table.add_column("Detail", style="green")
    
    table.add_row("From", GlobalState.start_location)

    if GlobalState.is_multi:
        table.add_row("To (Multi-Goal)", "".join(f"- {d.replace(", Batu, Indonesia", "").replace(", Malang, Indonesia", "").strip()}\n" for d in GlobalState.destination_location))
        
        sum_distance = 0
        total_visited = 0
        for i, r in enumerate(result):
            path, distance, visited = r
            sum_distance += distance
            total_visited += visited
            table.add_row(f"Route-{i+1}", "".join(f"- {p.replace(", Batu, Indonesia", "").replace(", Malang, Indonesia", "").strip()}\n" for p in path))
        
        table.add_row("Total distance", f"{sum_distance:.2f} meter")
        table.add_row("Time estimation", f"{sum_distance/GlobalState.avg_speed:.2f} minutes")  # Assume speed is 50 km/h (GlobalState.avg_speed m/minutes)
        table.add_row("Visited node", str(total_visited))
    else:
        path, distance, visited = result
        table.add_row("To", GlobalState.destination_location)
        table.add_row("Route", "".join(f"- {p.replace(", Batu, Indonesia", "").replace(", Malang, Indonesia", "").strip()}\n" for p in path))
        table.add_row("Total distance", f"{distance:.2f} meter")
        table.add_row("Time estimation", f"{distance/GlobalState.avg_speed:.2f} minutes")  # Assume speed is 50 km/h (GlobalState.avg_speed m/minutes)
        table.add_row("Visited node", str(visited))
    
    table.add_row("Time computation", f"{time_computation:.4f} seconds")
    
    console.print(table)
