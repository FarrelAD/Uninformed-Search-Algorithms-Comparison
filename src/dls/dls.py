import questionary
import random
import pandas as pd

df = None
matrix = None

def load_data() -> None:
    global df, matrix
    
    cities = ['Surabaya', 'Jakarta', 'Bandung', 'Semarang', 'Serang', 'Nganjuk', 'Malang', 'Tangerang', 'Bogor', 'Cirebon', 'Blitar']
    total_city = len(cities)
    matrix = [[0 for _ in range(total_city)] for _ in range(total_city)]

    matrix[0][3] = 360  # Surabaya to Semarang
    matrix[0][5] = 80   # Surabaya to Nganjuk
    matrix[0][6] = 90   # Surabaya to Malang

    matrix[1][2] = 150  # Jakarta to Bandung
    matrix[1][4] = 90   # Jakarta to Serang
    matrix[1][7] = 30   # Jakarta to Tangerang
    matrix[1][8] = 60   # Jakarta to Bogor

    matrix[2][1] = 150  # Bandung to Jakarta
    matrix[2][9] = 220  # Bandung to Cirebon

    matrix[3][0] = 360  # Semarang to Surabaya

    matrix[4][1] = 90   # Serang to Jakarta

    matrix[5][0] = 80   # Nganjuk to Surabaya

    matrix[6][0] = 90   # Malang to Surabaya
    matrix[6][10] = 100  # Malang to Blitar

    matrix[7][1] = 30   # Tangerang to Jakarta

    matrix[8][1] = 60   # Bogor to Jakarta

    matrix[9][2] = 220  # Cirebon to Bandung

    matrix[10][6] = 100  # Blitar to Malang

    df = pd.DataFrame(matrix, index=cities, columns=cities)

def run(start_city: str, destination_city: str) -> None:
    load_data()
    
    path = []
    
    print("Adjacency matrix with some cities not directly connected (in km):\n")
    print(df)

    max_depth = questionary.text("Enter the maximum depth for DLS:").ask()
    max_depth = int(max_depth)
    
    print(f"Index of {start_city}: {df.index.get_loc(start_city)}")
    print(f"Index of {destination_city}: {df.index.get_loc(destination_city)}")
    
    current_depth = 0
    path.append(start_city)
    def find_neighbours(current_city):
        nonlocal current_depth, path
        
        for i in df.index:
            if df.loc[i, current_city] > 0 and i not in path:
                print(f"Visiting: {i} (Depth: {current_depth})")
                
                current_depth += 1
                current_city = i
                path.append(current_city)
                
                if current_depth >= max_depth:
                    print(f"Max depth reached: {max_depth}")
                    return
                else:
                    find_neighbours(current_city)
    
    find_neighbours(start_city)
    
    print(f"Path found: {path}")
    print(f"Path length: {len(path)}")

def run_dls():
    """
    Execute the Depth Limited Search (DLS) algorithm.
    """
    print('DEPTH LIMITED SEARCH ALGORITHM')
