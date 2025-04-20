from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from rich.console import Console
from rich.panel import Panel
import questionary
import json
import os
from math import radians, sin, cos, sqrt, atan2

console = Console()

def haversine(lat1, lon1, lat2, lon2):
    """Menghitung jarak Haversine antara dua titik dalam meter"""
    R = 6371000  # Radius bumi dalam meter
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

class GrafDfs:
    def __init__(self):
        self.simpul = []  # Daftar simpul (node)
        self.daftar_ketetanggaan = defaultdict(list)  # Representasi adjacency list
        self.biaya = {}  # Biaya tepi (edge)
        self.simpul_awal = None
        self.simpul_akhir = None
        self.simpul_label = {}  # Mapping nama simpul panjang ke label pendek
        self.koordinat = {}  # Simpan koordinat untuk setiap simpul

    def tambah_simpul(self, nama_simpul, lat=None, lon=None):
        """Menambahkan simpul ke graf dengan koordinat opsional"""
        if nama_simpul not in self.simpul:
            self.simpul.append(nama_simpul)
            # Buat label pendek: ambil bagian pertama sebelum koma, batasi 15 karakter
            label = nama_simpul.split(",")[0][:15]
            self.simpul_label[nama_simpul] = label
            if lat is not None and lon is not None:
                self.koordinat[nama_simpul] = (lat, lon)

    def tambah_tepi(self, sumber, tujuan, biaya=1):
        """Menambahkan tepi antara simpul sumber dan tujuan dengan biaya tertentu"""
        if sumber not in self.simpul:
            self.tambah_simpul(sumber)
        if tujuan not in self.simpul:
            self.tambah_simpul(tujuan)
        
        # Tambahkan tepi ke kedua arah karena graf tidak berarah
        if tujuan not in self.daftar_ketetanggaan[sumber]:
            self.daftar_ketetanggaan[sumber].append(tujuan)
            self.biaya[(sumber, tujuan)] = biaya
        
        if sumber not in self.daftar_ketetanggaan[tujuan]:
            self.daftar_ketetanggaan[tujuan].append(sumber)
            self.biaya[(tujuan, sumber)] = biaya

    def tetapkan_simpul_awal(self, simpul):
        """Menetapkan simpul awal untuk algoritma pencarian"""
        if simpul in self.simpul:
            self.simpul_awal = simpul
            return True
        return False

    def tetapkan_simpul_akhir(self, simpul):
        """Menetapkan simpul akhir untuk algoritma pencarian"""
        if simpul in self.simpul:
            self.simpul_akhir = simpul
            return True
        return False

    def depth_first_search(self):
        """
        Melakukan pencarian depth-first dari simpul_awal ke simpul_akhir
        Mengembalikan tuple (jalur, total_biaya, semua_jalur, semua_biaya)
        """
        if not self.simpul_awal or not self.simpul_akhir:
            raise ValueError("Simpul awal dan simpul akhir harus ditetapkan sebelum menjalankan DFS")
        
        tumpukan = [(self.simpul_awal, [self.simpul_awal], 0)]  # (simpul_saat_ini, jalur, biaya_sejauh_ini)
        dikunjungi = set()
        semua_jalur = []
        semua_biaya = []
        
        while tumpukan:
            simpul_saat_ini, jalur, biaya = tumpukan.pop()  # DFS menggunakan tumpukan (LIFO)
            semua_jalur.append(jalur.copy())
            semua_biaya.append(biaya)
            
            if simpul_saat_ini == self.simpul_akhir:
                return jalur, biaya, semua_jalur, semua_biaya
            
            if simpul_saat_ini not in dikunjungi:
                dikunjungi.add(simpul_saat_ini)
                
                for tetangga in self.daftar_ketetanggaan[simpul_saat_ini]:
                    if tetangga not in dikunjungi:
                        biaya_tepi = self.biaya.get((simpul_saat_ini, tetangga), 1)
                        jalur_baru = jalur + [tetangga]
                        biaya_baru = biaya + biaya_tepi
                        tumpukan.append((tetangga, jalur_baru, biaya_baru))
        
        return None, None, semua_jalur, semua_biaya

    def to_networkx(self):
        """Mengonversi graf ke dalam format networkx untuk visualisasi"""
        G = nx.Graph()
        for simpul in self.simpul:
            G.add_node(simpul, label=self.simpul_label[simpul])
        for sumber in self.daftar_ketetanggaan:
            for tujuan in self.daftar_ketetanggaan[sumber]:
                if (sumber, tujuan) in self.biaya:
                    G.add_edge(sumber, tujuan, weight=self.biaya[(sumber, tujuan)])
        return G

def cetak_jalur(jalur, biaya):
    """Mencetak jalur dan biaya"""
    if jalur:
        console.print(Panel(f"[bold green]Jalur ditemukan: {' -> '.join(jalur)}[/bold green]"))
        console.print(f"Total biaya: [yellow]{biaya:.2f}[/yellow] meter")
    else:
        console.print(Panel("[bold red]Tidak ada jalur yang ditemukan[/bold red]"))

def cetak_proses_pencarian(semua_jalur, semua_biaya):
    """Mencetak proses pencarian"""
    console.print("\nProses pencarian:")
    for i, (jalur, biaya) in enumerate(zip(semua_jalur, semua_biaya)):
        console.print(f"Langkah {i+1}: Jalur = [green]{' -> '.join(jalur)}[/green], Biaya sejauh ini = [yellow]{biaya:.2f}[/yellow] meter")

def visualize_graph(G: nx.Graph, path=None, koordinat=None):
    """Menggambar graf menggunakan networkx dan matplotlib dengan posisi berdasarkan koordinat"""
    # Gunakan koordinat geografis untuk posisi simpul
    pos = {}
    for node in G.nodes():
        if node in koordinat:
            lat, lon = koordinat[node]
            pos[node] = (lon, -lat)  # Negatif latitude untuk membalikkan sumbu Y (agar sesuai peta)
    
    # Gambar simpul
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=800)
    
    # Gambar tepi
    edge_labels = {(u, v): f"{d['weight']:.0f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edges(G, pos, edge_color='orange', width=1)
    
    # Sorot jalur jika ada
    if path:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2)
    
    # Gunakan label pendek untuk simpul
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
    
    plt.title("Graph Visualization of Malang Locations")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.show()

def run_dfs_with_json(json_file, edges_file=None):
    """Menjalankan DFS dengan data dari JSON"""
    console.print(Panel("[bold cyan]PROGRAM ALGORITMA DFS DENGAN DATA JSON[/bold cyan]"))
    
    graf = GrafDfs()
    
    # Baca data simpul dan koordinat dari JSON
    try:
        with open(json_file, 'r') as f:
            nodes_data = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]File {json_file} tidak ditemukan![/red]")
        return
    except json.JSONDecodeError:
        console.print(f"[red]Format JSON tidak valid![/red]")
        return
    
    # Tambahkan simpul dari JSON
    for item in nodes_data:
        nama_simpul = item["name"]
        lat = item["latitude"]
        lon = item["longitude"]
        graf.tambah_simpul(nama_simpul, lat, lon)
    
    # Baca data tepi dari file edges (JSON pertama) jika ada
    if edges_file:
        try:
            with open(edges_file, 'r') as f:
                edges_data = json.load(f)
        except FileNotFoundError:
            console.print(f"[red]File tepi {edges_file} tidak ditemukan! Menggunakan Haversine sebagai gantinya.[/red]")
            edges_data = None
        except json.JSONDecodeError:
            console.print(f"[red]Format JSON tepi tidak valid! Menggunakan Haversine sebagai gantinya.[/red]")
            edges_data = None
    else:
        edges_data = None
    
    # Tambahkan tepi
    if edges_data:
        # Gunakan tepi dari JSON pertama
        for item in edges_data:
            simpul_sumber = item["node"]
            for tetangga in item["branch"]:
                simpul_tujuan = tetangga["node"]
                biaya = tetangga["distance"]
                if biaya > 0:  # Abaikan jarak 0
                    graf.tambah_tepi(simpul_sumber, simpul_tujuan, biaya)
    else:
        # Gunakan Haversine untuk membuat tepi
        max_distance = 5000  # Ambang batas jarak maksimum untuk tepi (5 km)
        for i, item1 in enumerate(nodes_data):
            simpul1 = item1["name"]
            lat1, lon1 = graf.koordinat[simpul1]
            for item2 in nodes_data[i+1:]:
                simpul2 = item2["name"]
                lat2, lon2 = graf.koordinat[simpul2]
                # Hanya hubungkan jika berada di wilayah yang sama (Malang atau Batu)
                if ("Malang" in simpul1 and "Malang" in simpul2) or ("Batu" in simpul1 and "Batu" in simpul2):
                    jarak = haversine(lat1, lon1, lat2, lon2)
                    if jarak <= max_distance:
                        graf.tambah_tepi(simpul1, simpul2, jarak)

    # Tampilkan daftar simpul yang tersedia
    console.print("\nDaftar simpul yang tersedia:")
    for simpul in graf.simpul:
        console.print(f"- {simpul}")
    
    # Pilih simpul awal menggunakan menu
    simpul_awal = questionary.select(
        "Pilih simpul awal:",
        choices=graf.simpul
    ).ask()
    if not graf.tetapkan_simpul_awal(simpul_awal):
        console.print(f"[red]Simpul awal tidak valid![/red]")
        return
    
    # Pilih simpul akhir menggunakan menu
    simpul_akhir = questionary.select(
        "Pilih simpul akhir:",
        choices=[s for s in graf.simpul if s != simpul_awal]
    ).ask()
    if not graf.tetapkan_simpul_akhir(simpul_akhir):
        console.print(f"[red]Simpul akhir tidak valid![/red]")
        return
    
    # Jalankan DFS
    try:
        console.print("\n=== Menjalankan Algoritma DFS ===")
        jalur, biaya, semua_jalur, semua_biaya = graf.depth_first_search()
        cetak_jalur(jalur, biaya)
        if questionary.confirm("Tampilkan proses pencarian?").ask():
            cetak_proses_pencarian(semua_jalur, semua_biaya)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return
    
    # Visualisasi graf
    if questionary.confirm("Apakah Anda ingin melihat visualisasi graf dan jalur?").ask():
        G = graf.to_networkx()
        visualize_graph(G, path=jalur, koordinat=graf.koordinat)
    
    # Simpan hasil ke file
    if jalur and questionary.confirm("Simpan hasil ke file?").ask():
        output_file = os.path.join(os.path.dirname(json_file), "hasil_dfs.txt")
        with open(output_file, "w") as f:
            f.write(f"Jalur: {' -> '.join(jalur)}\n")
            f.write(f"Total biaya: {biaya:.2f} meter\n")
        console.print(f"[green]Hasil disimpan ke {output_file}[/green]")
    
    console.print("\n=== Program Selesai ===")

if __name__ == "__main__":
    json_file = r"D:\kuliah\Semester 4\AI\Python\Uninformed-Search-Algorithms-Comparison\data\malang_locations.json"
    edges_file = r"D:\kuliah\Semester 4\AI\Python\Uninformed-Search-Algorithms-Comparison\data\malang_graph.json"
    run_dfs_with_json(json_file, edges_file)