import time
from rich.console import Console
from rich.panel import Panel
import questionary
from collections import defaultdict, deque
from math import radians, cos, sin, asin, sqrt  # Added math imports

from helpers.result_helper import show_result, visualize_route
from store.states import GlobalState

from pprint import pprint

console = Console()

class GrafBfs:
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
        
        # Periksa apakah branch kosong dan buat koneksi berdasarkan data lokasi jika perlu
        all_empty_branches = all(len(item.get("branch", [])) == 0 for item in graph_data)
        
        if all_empty_branches and hasattr(GlobalState, 'location_nodes') and GlobalState.location_nodes:
            # Fungsi untuk menghitung jarak Haversine antara dua titik geografis
            def haversine(lat1, lon1, lat2, lon2):
                """Menghitung jarak antara dua titik koordinat geografis dalam meter"""
                # Konversi koordinat ke radian
                lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
                
                # Formula Haversine
                dlon = lon2 - lon1 
                dlat = lat2 - lat1 
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a)) 
                r = 6371000  # Radius bumi dalam meter
                return c * r
            
            # Buat dictionary untuk menyimpan lokasi setiap node
            node_locations = {}
            for location in GlobalState.location_nodes:
                node_locations[location["name"]] = (location["latitude"], location["longitude"])
            
            # Tetapkan threshold jarak untuk menentukan koneksi antar node
            # Titik-titik yang jaraknya kurang dari threshold akan dianggap terhubung
            threshold_distance = 5000  # 5 km dalam meter
            
            # Buat koneksi antar node berdasarkan jarak geografis
            for i, node1 in enumerate(self.simpul):
                if node1 not in node_locations:
                    continue
                    
                for node2 in self.simpul[i+1:]:  # Hindari duplikasi
                    if node2 not in node_locations:
                        continue
                    
                    lat1, lon1 = node_locations[node1]
                    lat2, lon2 = node_locations[node2]
                    
                    distance = haversine(lat1, lon1, lat2, lon2)
                    
                    if distance <= threshold_distance:
                        # Tambahkan koneksi dua arah
                        if node2 not in self.daftar_ketetanggaan[node1]:
                            self.daftar_ketetanggaan[node1].append(node2)
                            self.biaya[(node1, node2)] = distance
                        
                        if node1 not in self.daftar_ketetanggaan[node2]:
                            self.daftar_ketetanggaan[node2].append(node1)
                            self.biaya[(node2, node1)] = distance
        else:
            # Tambahkan tepi dari data branch yang ada jika branch tidak kosong
            for item in graph_data:
                simpul_sumber = item["node"]
                for tetangga in item.get("branch", []):
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

    def breadth_first_search(self):
        """
        Melakukan pencarian breadth-first dari simpul_awal ke simpul_akhir
        Mengembalikan tuple (jalur, total_biaya, semua_jalur)
        """
        if not self.simpul_awal or not self.simpul_akhir:
            raise ValueError("Simpul awal dan simpul akhir harus ditetapkan sebelum menjalankan BFS")
        
        # Inisialisasi struktur data
        antrian = deque([(self.simpul_awal, [self.simpul_awal], 0)])  # (simpul_saat_ini, jalur, biaya_sejauh_ini)
        dikunjungi = set([self.simpul_awal])
        semua_jalur = []
        
        while antrian:
            simpul_saat_ini, jalur, biaya = antrian.popleft()  # BFS menggunakan antrian (FIFO)
            semua_jalur.append(jalur.copy())
            
            if simpul_saat_ini == self.simpul_akhir:
                return jalur, biaya, semua_jalur
            
            for tetangga in self.daftar_ketetanggaan[simpul_saat_ini]:
                if tetangga not in dikunjungi:
                    dikunjungi.add(tetangga)
                    biaya_tepi = self.biaya.get((simpul_saat_ini, tetangga), 1)
                    jalur_baru = jalur + [tetangga]
                    biaya_baru = biaya + biaya_tepi
                    antrian.append((tetangga, jalur_baru, biaya_baru))
        
        return None, None, semua_jalur

def search(start: str = None, goal: str = None) -> tuple[list[str], int, list[str]]:
    path = []
    visited = []

    # Pastikan malang_graph ada
    if not GlobalState.malang_graph:
        console.print("[red]Data graf tidak ditemukan di GlobalState![/red]")
        return path, 0, visited

    # Buat graf dari data GlobalState
    graf = GrafBfs(GlobalState.malang_graph)

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

    # Jalankan BFS
    try:
        jalur, biaya, semua_jalur = graf.breadth_first_search()
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
    graf = GrafBfs(GlobalState.malang_graph)

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

    # Lakukan BFS untuk setiap tujuan secara berurutan
    current_start = GlobalState.start_location
    for goal in GlobalState.destination_location:
        graf.tetapkan_simpul_awal(current_start)
        graf.tetapkan_simpul_akhir(goal)

        try:
            jalur, biaya, jalur_sebagian = graf.breadth_first_search()
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




def run_bfs() -> tuple[list[str], int, list[str]]:
    """
    Execute the Breadth First Search (BFS) algorithm.
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