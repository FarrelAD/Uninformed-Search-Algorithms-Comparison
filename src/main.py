from rich.console import Console
import questionary

from helpers.dataset_helper import load_malang_osm_data
from helpers.output_helper import show_banner
from menu import find_route_destination, visualize_graph_networkx


console = Console()

def main():
    """Main function to run the application"""
    show_banner('EXPEDITION ROUTE FINDER')
    
    G, malang_graph, location_nodes = load_malang_osm_data()
    
    while True:
        choice = questionary.select(
            "Select menu:",
            choices=[
                "1. Find delivery route",
                "2. View location graph",
                "3. Exit"
            ]).ask()
        
        if choice == "1. Find delivery route":
            find_route_destination(G, malang_graph, location_nodes)
        elif choice == "2. View location graph":
            visualize_graph_networkx(malang_graph)
        elif choice == "3. Exit":
            console.print("[bold green]Thanks for using this app![/bold green]")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Program stopped by user.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An error occurred: {str(e)}[/bold red]")
