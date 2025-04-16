from collections import defaultdict, deque

class GrafBfs:
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
    
    def breadth_first_search(self):
        """
        Melakukan pencarian breadth-first dari simpul_awal ke simpul_akhir
        Mengembalikan tuple (jalur, total_biaya) jika jalur ditemukan, sebaliknya mengembalikan (None, None)
        """
        if not self.simpul_awal or not self.simpul_akhir:
            raise ValueError("Simpul awal dan simpul akhir harus ditetapkan sebelum menjalankan BFS")
        
        # Inisialisasi struktur data
        antrian = deque([(self.simpul_awal, [self.simpul_awal], 0)])  # (simpul_saat_ini, jalur, biaya_sejauh_ini)
        dikunjungi = set([self.simpul_awal])
        
        # Untuk melacak proses pencarian
        semua_jalur = []
        semua_biaya = []
        
        while antrian:
            simpul_saat_ini, jalur, biaya = antrian.popleft()
            semua_jalur.append(jalur.copy())
            semua_biaya.append(biaya)
            
            # Periksa apakah kita telah mencapai simpul akhir
            if simpul_saat_ini == self.simpul_akhir:
                return jalur, biaya, semua_jalur, semua_biaya
            
            # Jelajahi tetangga
            for tetangga in self.daftar_ketetanggaan[simpul_saat_ini]:
                if tetangga not in dikunjungi:
                    dikunjungi.add(tetangga)
                    biaya_tepi = self.biaya.get((simpul_saat_ini, tetangga), 1)
                    jalur_baru = jalur + [tetangga]
                    biaya_baru = biaya + biaya_tepi
                    antrian.append((tetangga, jalur_baru, biaya_baru))
        
        # Jika tidak ada jalur yang ditemukan
        return None, None, semua_jalur, semua_biaya

def cetak_jalur(jalur, biaya):
    """Mencetak jalur dan biaya"""
    if jalur:
        print(f"\nJalur ditemukan: {' -> '.join(jalur)}")
        print(f"Total biaya: {biaya}")
    else:
        print("\nTidak ada jalur yang ditemukan")

def cetak_proses_pencarian(semua_jalur, semua_biaya):
    """Mencetak proses pencarian"""
    print("\nProses pencarian:")
    for i, (jalur, biaya) in enumerate(zip(semua_jalur, semua_biaya)):
        print(f"Langkah {i+1}: Jalur = {jalur}, Biaya sejauh ini = {biaya}")

def input_integer(pesan):
    """Meminta input integer dari pengguna"""
    while True:
        try:
            nilai = int(input(pesan))
            return nilai
        except ValueError:
            print("Masukkan nilai numerik yang valid!")

def main():
    print("=== PROGRAM ALGORITMA BFS ===")
    graf = GrafBfs()
    
    # Input jumlah simpul
    jumlah_simpul = input_integer("Masukkan jumlah simpul: ")
    
    # Input nama-nama simpul
    print("\nMasukkan nama untuk setiap simpul:")
    for i in range(jumlah_simpul):
        nama_simpul = input(f"Nama simpul {i+1}: ")
        graf.tambah_simpul(nama_simpul)
    
    # Input jumlah tepi
    print("\n--- Menentukan Hubungan Antar Simpul ---")
    jumlah_tepi = input_integer("Masukkan jumlah tepi/hubungan: ")
    
    # Input tepi dan biaya
    print("\nMasukkan tepi dan biayanya:")
    for i in range(jumlah_tepi):
        while True:
            sumber = input(f"Tepi {i+1} - Simpul sumber: ")
            if sumber in graf.simpul:
                break
            print(f"Simpul '{sumber}' tidak ada! Pilih dari: {graf.simpul}")
        
        while True:
            tujuan = input(f"Tepi {i+1} - Simpul tujuan: ")
            if tujuan in graf.simpul:
                break
            print(f"Simpul '{tujuan}' tidak ada! Pilih dari: {graf.simpul}")
        
        biaya = input_integer(f"Tepi {i+1} - Biaya: ")
        graf.tambah_tepi(sumber, tujuan, biaya)
        print(f"Tepi ditambahkan: {sumber} <-> {tujuan} (biaya: {biaya})")
    
    # Input simpul awal dan akhir
    print("\n--- Menentukan Simpul Awal dan Akhir ---")
    while True:
        simpul_awal = input("Masukkan simpul awal: ")
        if graf.tetapkan_simpul_awal(simpul_awal):
            break
        print(f"Simpul '{simpul_awal}' tidak ada! Pilih dari: {graf.simpul}")
    
    while True:
        simpul_akhir = input("Masukkan simpul akhir: ")
        if graf.tetapkan_simpul_akhir(simpul_akhir):
            break
        print(f"Simpul '{simpul_akhir}' tidak ada! Pilih dari: {graf.simpul}")
    
    # Jalankan BFS dan tampilkan hasilnya
    try:
        print("\n=== Menjalankan Algoritma BFS ===")
        jalur, biaya, semua_jalur, semua_biaya = graf.breadth_first_search()
        cetak_jalur(jalur, biaya)
        cetak_proses_pencarian(semua_jalur, semua_biaya)
    except ValueError as e:
        print(f"Error: {e}")

    print("\n=== Program Selesai ===")

if __name__ == "__main__":
    main()