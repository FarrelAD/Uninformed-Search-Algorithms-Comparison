from rich.console import Console
from rich.panel import Panel
from pyfiglet import Figlet

console = Console()

def show_banner(title: str) -> None:
    """Show a banner with the given title."""
    f = Figlet(font='slant')
    banner = f.renderText(title)
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print(Panel("[bold yellow]GOODS DELIVERY ROUTE SEARCH SYSTEM IN MALANG RAYA[/bold yellow]\n"
                      "[green]AN IMPLEMENTATION OF UNINFORMED SEARCH ALGORITHMS[/green]\n"
                      "[blue]Midterm Test Artificial Inteligence - 2025[/blue]"))