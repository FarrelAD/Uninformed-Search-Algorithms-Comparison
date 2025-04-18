import questionary
from rich.console import Console
from rich.panel import Panel
from pyfiglet import Figlet

from helpers.dataset_helper import load_malang_osm_data
from menu import find_route_destination, visualize_graph_networkx


console = Console()


def show_banner():
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
    
    G, malang_graph, location_nodes = load_malang_osm_data()
    
    while True:
        choice = questionary.select(
            "Pilih Menu:",
            choices=[
                "1. Cari Rute Pengiriman",
                "2. Lihat Graf Lokasi",
                "3. Keluar"
            ]).ask()
        
        if choice == "1. Cari Rute Pengiriman":
            find_route_destination(G, malang_graph, location_nodes)
        elif choice == "2. Lihat Graf Lokasi":
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