import time
import questionary
from rich.console import Console
from helpers.map_helper import show_banner, load_malang_osm_data, tampilkan_hasil, visualize_route, visualize_graph_networkx

from ucs.ucs import UniformCostSearch

console = Console()

def main():
    """Fungsi utama untuk menjalankan aplikasi"""
    show_banner()
    
    # Muat data OSM
    G, malang_graph, location_nodes = load_malang_osm_data()
    
    # Definisikan waktu maksimal operasional kendaraan (dalam menit)
    max_operating_time = 120  # 2 jam
    
    while True:
        # Tampilkan menu utama
        choice = questionary.select(
            "Pilih Menu:",
            choices=[
                "1. Cari Rute Pengiriman",
                "2. Lihat Graf Lokasi",
                "3. Keluar"
            ]).ask()
        
        if choice == "1. Cari Rute Pengiriman":
            # Tampilkan daftar lokasi
            daftar_lokasi = sorted(malang_graph.keys())
            
            # Pilih lokasi awal
            console.print("\n[bold cyan]Pilih Lokasi Awal dan Tujuan[/bold cyan]")
            
            lokasi_awal = questionary.select(
                "Pilih lokasi awal:",
                choices=daftar_lokasi
            ).ask()
            
            # Tanya apakah ini pencarian multi-tujuan
            is_multi = questionary.confirm("Apakah Anda ingin melakukan pengiriman ke beberapa tujuan (multi-goal)?").ask()
            
            if is_multi:
                # Multi-goal: pilih beberapa tujuan
                lokasi_tujuan = []
                jumlah_tujuan = questionary.text(
                    "Berapa jumlah tujuan yang ingin dikunjungi?",
                    validate=lambda text: text.isdigit() and 1 <= int(text) <= 5,
                    instruction="(Masukkan angka 1-5)"
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
                # Single-goal: pilih satu tujuan
                lokasi_tujuan = questionary.select(
                    "Pilih lokasi tujuan:",
                    choices=[loc for loc in daftar_lokasi if loc != lokasi_awal]
                ).ask()
                
                # Memastikan lokasi awal dan tujuan berbeda
                if lokasi_awal == lokasi_tujuan:
                    console.print("[bold red]Lokasi awal dan tujuan sama. Silakan pilih lokasi yang berbeda.[/bold red]")
                    continue
            
            # Tanya pengguna apakah ingin melihat ilustrasi proses
            tampilkan_proses = questionary.confirm("Apakah Anda ingin melihat ilustrasi proses pencarian?").ask()
            
            # Inisialisasi algoritma UCS
            ucs = UniformCostSearch(malang_graph)
            
            # Lakukan pencarian dan hitung waktu
            start_time = time.time()
            
            if is_multi:
                hasil = ucs.search_multigoal(lokasi_awal, lokasi_tujuan, tampilkan_proses)
            else:
                hasil = ucs.search(lokasi_awal, lokasi_tujuan, tampilkan_proses)
                
            end_time = time.time()
            waktu_komputasi = end_time - start_time
            
            # Tampilkan hasil
            route = tampilkan_hasil(lokasi_awal, lokasi_tujuan, hasil, waktu_komputasi, is_multi)
            
            # Cek batas waktu operasional
            if hasil:
                path, cost, _ = hasil
                estimated_time = cost / 833.33  # Asumsi kecepatan 50 km/jam (833.33 m/menit)
                
                if estimated_time > max_operating_time:
                    console.print(f"[bold red]Peringatan: Rute ini membutuhkan waktu {estimated_time:.2f} menit, "
                                f"melebihi batas waktu operasional {max_operating_time} menit![/bold red]")
            
            # Tanya pengguna apakah ingin melihat rute pada peta
            if route and G is not None and location_nodes is not None:
                if questionary.confirm("Apakah Anda ingin melihat visualisasi rute pada peta?").ask():
                    visualize_route(G, location_nodes, route)
        
        elif choice == "2. Lihat Graf Lokasi":
            console.print("\n[bold cyan]Visualisasi Graf Lokasi[/bold cyan]")
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