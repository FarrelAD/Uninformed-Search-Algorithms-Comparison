import time
from rich.console import Console
from rich.panel import Panel
import questionary
from collections import defaultdict

from helpers.result_helper import show_result, visualize_route
from store.states import GlobalState

from pprint import pprint

console = Console()

class GrafDfs:
    def __init__(self, graph_data):
        self.daftar_ketetanggaan = defaultdict(list)  # Representasi adjacency list
        self.biaya = {}  # Biaya tepi (edge)
        self.simpul = []  # Daftar simpul
        self.simpul_awal = None
        self.simpul_akhir = None
        self._build_graph(graph_data)

    def _build_graph(self, graph_data):
        """Membangun graf dari data GlobalState.malang_graph"""
        # Tambahkan semua simpul
        for item in graph_data:
            node = item["node"]
            if node not in self.simpul:
                self.simpul.append(node)

        # Tambahkan tepi dari data branch
        for item in graph_data:
            simpul_sumber = item["node"]
            for tetangga in item["branch"]:
                simpul_tujuan = tetangga["node"]
                biaya = tetangga["distance"]
                if biaya > 0:  # Abaikan jarak 0
                    if simpul_tujuan not in self.daftar_ketetanggaan[simpul_sumber]:
                        self.daftar_ketetanggaan[simpul_sumber].append(simpul_tujuan)
                        self.biaya[(simpul_sumber, simpul_tujuan)] = biaya
                    if simpul_sumber not in self.daftar_ketetanggaan[simpul_tujuan]:
                        self.daftar_ketetanggaan[simpul_tujuan].append(simpul_sumber)
                        self.biaya[(simpul_tujuan, simpul_sumber)] = biaya

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
        Mengembalikan tuple (jalur, total_biaya, semua_jalur)
        """
        if not self.simpul_awal or not self.simpul_akhir:
            raise ValueError("Simpul awal dan simpul akhir harus ditetapkan sebelum menjalankan DFS")

        tumpukan = [(self.simpul_awal, [self.simpul_awal], 0)]  # (simpul_saat_ini, jalur, biaya_sejauh_ini)
        dikunjungi = set()
        semua_jalur = []

        while tumpukan:
            simpul_saat_ini, jalur, biaya = tumpukan.pop()  # DFS menggunakan tumpukan (LIFO)
            semua_jalur.append(jalur.copy())

            if simpul_saat_ini == self.simpul_akhir:
                return jalur, biaya, semua_jalur

            if simpul_saat_ini not in dikunjungi:
                dikunjungi.add(simpul_saat_ini)

                for tetangga in self.daftar_ketetanggaan[simpul_saat_ini]:
                    if tetangga not in dikunjungi:
                        biaya_tepi = self.biaya.get((simpul_saat_ini, tetangga), 1)
                        jalur_baru = jalur + [tetangga]
                        biaya_baru = biaya + biaya_tepi
                        tumpukan.append((tetangga, jalur_baru, biaya_baru))

        return None, None, semua_jalur

def search(start: str = None, goal: str = None) -> tuple[list[str], int, list[str]]:
    path = []
    visited = []

    # Pastikan malang_graph ada
    if not GlobalState.malang_graph:
        console.print("[red]Data graf tidak ditemukan di GlobalState![/red]")
        return path, 0, visited

    # Buat graf dari data GlobalState
    graf = GrafDfs(GlobalState.malang_graph)

    # Tetapkan simpul awal dan akhir
    if start and goal:
        graf.tetapkan_simpul_awal(start)
        graf.tetapkan_simpul_akhir(goal)
    else:
        # Jika start atau goal tidak diberikan, gunakan nilai dari GlobalState
        if not GlobalState.start_location or not GlobalState.destination_location:
            console.print("[red]Simpul awal atau akhir tidak ditemukan di GlobalState![/red]")
            return path, 0, visited
        graf.tetapkan_simpul_awal(GlobalState.start_location)
        graf.tetapkan_simpul_akhir(GlobalState.destination_location)

    # Jalankan DFS
    try:
        jalur, biaya, semua_jalur = graf.depth_first_search()
        if jalur:
            path = jalur
            visited = semua_jalur
            return path, int(biaya), visited
        else:
            console.print("[red]Tidak ada jalur yang ditemukan![/red]")
            return path, 0, visited
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return path, 0, visited

def search_multigoal() -> tuple[list[str], int, list[str]]:
    path = []
    visited = []

    # Pastikan malang_graph ada
    if not GlobalState.malang_graph:
        console.print("[red]Data graf tidak ditemukan di GlobalState![/red]")
        return path, 0, visited

    # Buat graf dari data GlobalState
    graf = GrafDfs(GlobalState.malang_graph)

    # Pastikan ada simpul awal dan beberapa tujuan
    if not GlobalState.start_location or not GlobalState.destination_location:
        console.print("[red]Simpul awal atau tujuan tidak ditemukan di GlobalState![/red]")
        return path, 0, visited

    # Pastikan destination_location adalah list untuk mode multi
    if not isinstance(GlobalState.destination_location, list):
        console.print("[red]Destination harus berupa list untuk mode multi-goal![/red]")
        return path, 0, visited

    # Inisialisasi variabel
    total_biaya = 0
    semua_jalur = []
    jalur_lengkap = [GlobalState.start_location]

    # Lakukan DFS untuk setiap tujuan secara berurutan
    current_start = GlobalState.start_location
    for goal in GlobalState.destination_location:
        graf.tetapkan_simpul_awal(current_start)
        graf.tetapkan_simpul_akhir(goal)

        try:
            jalur, biaya, jalur_sebagian = graf.depth_first_search()
            if not jalur:
                console.print(f"[red]Tidak ada jalur dari {current_start} ke {goal}![/red]")
                return path, 0, visited

            # Tambahkan jalur (tanpa simpul awal yang duplikat)
            jalur_lengkap.extend(jalur[1:])
            total_biaya += biaya
            semua_jalur.extend(jalur_sebagian)

            # Simpul tujuan saat ini menjadi simpul awal untuk langkah berikutnya
            current_start = goal

        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            return path, 0, visited

    path = jalur_lengkap
    visited = semua_jalur
    return path, int(total_biaya), visited

def run_dfs() -> tuple[list[str], int, list[str]]:
    """
    Execute the Depth First Search (DFS) algorithm.
    """
    
    start_time = time.time()
    
    if GlobalState.is_multi:
        result = search_multigoal()
    else:
        result = search()
        
    end_time = time.time()
    time_computation = end_time - start_time
    
    show_result(result, time_computation)
    
    if result:
        _, cost, _ = result
        estimated_time = cost / 833.33  # Assume speed is 50 km/h (833.33 m/minutes)
        
        if estimated_time > GlobalState.max_operating_time:
            console.print(f"[bold red]WARNING!: This route takes {estimated_time:.2f} minutes, "
                        f"melebihi batas waktu operasional {GlobalState.max_operating_time} menit![/bold red]")

    if result[0] and GlobalState.G is not None and GlobalState.location_nodes is not None:
        if questionary.confirm("Apakah Anda ingin melihat visualisasi rute pada peta?").ask():
            visualize_route(result[0])

    return result