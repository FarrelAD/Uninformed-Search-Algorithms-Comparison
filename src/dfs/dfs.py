from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from rich.console import Console
from rich.panel import Panel
import questionary

console = Console()

class GrafDfs:
    def __init__(self):
        self.simpul = []  # Daftar simpul (node)
        self.daftar_ketetanggaan = defaultdict(list)  # Representasi adjacency list
        self.biaya = {}  # Biaya tepi (edge)
        self.simpul_awal = None
        self.simpul_akhir = None

    def tambah_simpul(self, nama_simpul):
        """Menambahkan simpul ke graf"""
        if nama_simpul not in self.simpul:
            self.simpul.append(nama_simpul)
    
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
        Mengembalikan tuple (jalur, total_biaya, semua_jalur, semua_biaya) jika jalur ditemukan,
        sebaliknya mengembalikan (None, None, semua_jalur, semua_biaya)
        """
        if not self.simpul_awal or not self.simpul_akhir:
            raise ValueError("Simpul awal dan simpul akhir harus ditetapkan sebelum menjalankan DFS")
        
        # Inisialisasi struktur data
        tumpukan = [(self.simpul_awal, [self.simpul_awal], 0)]  # (simpul_saat_ini, jalur, biaya_sejauh_ini)
        dikunjungi = set()
        semua_jalur = []
        semua_biaya = []
        
        while tumpukan:
            simpul_saat_ini, jalur, biaya = tumpukan.pop()  # DFS menggunakan tumpukan (LIFO)
            semua_jalur.append(jalur.copy())
            semua_biaya.append(biaya)
            
            # Periksa apakah kita telah mencapai simpul akhir
            if simpul_saat_ini == self.simpul_akhir:
                return jalur, biaya, semua_jalur, semua_biaya
            
            # Tandai simpul saat ini sebagai dikunjungi
            if simpul_saat_ini not in dikunjungi:
                dikunjungi.add(simpul_saat_ini)
                
                # Jelajahi tetangga
                for tetangga in self.daftar_ketetanggaan[simpul_saat_ini]:
                    if tetangga not in dikunjungi:
                        biaya_tepi = self.biaya.get((simpul_saat_ini, tetangga), 1)
                        jalur_baru = jalur + [tetangga]
                        biaya_baru = biaya + biaya_tepi
                        tumpukan.append((tetangga, jalur_baru, biaya_baru))
        
        # Jika tidak ada jalur yang ditemukan
        return None, None, semua_jalur, semua_biaya
    
    def to_networkx(self):
        """Mengonversi graf ke dalam format networkx untuk visualisasi"""
        G = nx.Graph()
        # Tambahkan simpul
        for simpul in self.simpul:
            G.add_node(simpul)
        # Tambahkan tepi dengan bobot
        for sumber in self.daftar_ketetanggaan:
            for tujuan in self.daftar_ketetanggaan[sumber]:
                if (sumber, tujuan) in self.biaya:  # Pastikan hanya menambahkan tepi sekali
                    G.add_edge(sumber, tujuan, weight=self.biaya[(sumber, tujuan)])
        return G

def cetak_jalur(jalur, biaya):
    """Mencetak jalur dan biaya"""
    if jalur:
        console.print(Panel(f"[bold green]Jalur ditemukan: {' -> '.join(jalur)}[/bold green]"))
        console.print(f"Total biaya: [yellow]{biaya}[/yellow]")
    else:
        console.print(Panel("[bold red]Tidak ada jalur yang ditemukan[/bold red]"))

def cetak_proses_pencarian(semua_jalur, semua_biaya):
    """Mencetak proses pencarian"""
    console.print("\nProses pencarian:")
    for i, (jalur, biaya) in enumerate(zip(semua_jalur, semua_biaya)):
        console.print(f"Langkah {i+1}: Jalur = [green]{' -> '.join(jalur)}[/green], Biaya sejauh ini = [yellow]{biaya}[/yellow]")

def input_integer(pesan):
    """Meminta input integer dari pengguna"""
    while True:
        try:
            nilai = int(input(pesan))
            return nilai
        except ValueError:
            print("Masukkan nilai numerik yang valid!")

def visualize_graph(G: nx.Graph, path=None):
    """
    Menggambar graf menggunakan networkx dan matplotlib.
    Jika path diberikan, jalur tersebut akan disorot.
    """
    pos = nx.spring_layout(G)  # Posisi simpul menggunakan spring layout
    
    # Gambar simpul
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
    
    # Gambar tepi
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edges(G, pos, edge_color='black', width=1)
    
    # Jika ada jalur, sorot jalur tersebut
    if path:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2)
    
    # Gambar label simpul dan bobot tepi
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    plt.title("Visualisasi Graf dan Jalur (Jalur Merah jika Ditemukan)")
    plt.show()

def run_dfs():
    """
    Execute the Depth First Search (DFS) algorithm and visualize the graph.
    """
    console.print(Panel("[bold cyan]PROGRAM ALGORITMA DFS DENGAN VISUALISASI GRAF[/bold cyan]"))
    
    graf = GrafDfs()
    
    # Input jumlah simpul
    jumlah_simpul = input_integer("Masukkan jumlah simpul: ")
    
    # Input nama-nama simpul
    console.print("\nMasukkan nama untuk setiap simpul:")
    for i in range(jumlah_simpul):
        nama_simpul = input(f"Nama simpul {i+1}: ")
        graf.tambah_simpul(nama_simpul)
    
    # Input jumlah tepi
    console.print("\n--- Menentukan Hubungan Antar Simpul ---")
    jumlah_tepi = input_integer("Masukkan jumlah tepi/hubungan: ")
    
    # Input tepi dan biaya
    console.print("\nMasukkan tepi dan biayanya:")
    for i in range(jumlah_tepi):
        while True:
            sumber = input(f"Tepi {i+1} - Simpul sumber: ")
            if sumber in graf.simpul:
                break
            console.print(f"[red]Simpul '{sumber}' tidak ada! Pilih dari: {graf.simpul}[/red]")
        
        while True:
            tujuan = input(f"Tepi {i+1} - Simpul tujuan: ")
            if tujuan in graf.simpul:
                break
            console.print(f"[red]Simpul '{tujuan}' tidak ada! Pilih dari: {graf.simpul}[/red]")
        
        biaya = input_integer(f"Tepi {i+1} - Biaya: ")
        graf.tambah_tepi(sumber, tujuan, biaya)
        console.print(f"Tepi ditambahkan: [cyan]{sumber} <-> {tujuan}[/cyan] (biaya: [yellow]{biaya}[/yellow])")
    
    # Input simpul awal dan akhir
    console.print("\n--- Menentukan Simpul Awal dan Akhir ---")
    while True:
        simpul_awal = input("Masukkan simpul awal: ")
        if graf.tetapkan_simpul_awal(simpul_awal):
            break
        console.print(f"[red]Simpul '{simpul_awal}' tidak ada! Pilih dari: {graf.simpul}[/red]")
    
    while True:
        simpul_akhir = input("Masukkan simpul akhir: ")
        if graf.tetapkan_simpul_akhir(simpul_akhir):
            break
        console.print(f"[red]Simpul '{simpul_akhir}' tidak ada! Pilih dari: {graf.simpul}[/red]")
    
    # Jalankan DFS dan tampilkan hasilnya
    try:
        console.print("\n=== Menjalankan Algoritma DFS ===")
        jalur, biaya, semua_jalur, semua_biaya = graf.depth_first_search()
        cetak_jalur(jalur, biaya)
        cetak_proses_pencarian(semua_jalur, semua_biaya)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return
    
    # Visualisasi graf
    if questionary.confirm("Apakah Anda ingin melihat visualisasi graf dan jalur?").ask():
        G = graf.to_networkx()
        visualize_graph(G, path=jalur)

    console.print("\n=== Program Selesai ===")

if __name__ == "__main__":
    run_dfs()