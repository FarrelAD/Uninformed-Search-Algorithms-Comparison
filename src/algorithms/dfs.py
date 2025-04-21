import time
from rich.console import Console
from rich.panel import Panel
import questionary

from helpers.result_helper import show_result, visualize_route
from store.states import GlobalState

console = Console()

def search(start: str = None, goal: str = None) -> tuple[list[str], int, list[str]]:
    """
    Run single destination search
    """
    start = start if start is not None else GlobalState.start_location
    goal = goal if goal is not None else GlobalState.destination_location

    if GlobalState.show_process:
        console.print(Panel(f"[bold cyan]ILLUSTRATION OF SEARCH PROCESS DEPTH-FIRST SEARCH[/bold cyan]"))
        console.print(f"Mencari rute dari [green]{start}[/green] ke [green]{goal}[/green]...")

    # Initialize the variables
    tumpukan = [(start, [start], 0)]  # (current_node, path, current_cost)
    dikunjungi = set()
    semua_jalur = []

    # Ensure the graph data exists
    if not GlobalState.malang_graph:
        console.print("[red]Data graf tidak ditemukan di GlobalState![/red]")
        return [], 0, len([])

    # Perform DFS search
    while tumpukan:
        simpul_saat_ini, jalur, biaya = tumpukan.pop()  # DFS with stack (LIFO)
        semua_jalur.append(jalur.copy())

        if simpul_saat_ini == goal:
            return jalur, biaya, len(semua_jalur)

        if simpul_saat_ini not in dikunjungi:
            dikunjungi.add(simpul_saat_ini)

            # Get neighbors from graph
            for item in GlobalState.malang_graph:
                if item["node"] == simpul_saat_ini:
                    for tetangga in item["branch"]:
                        if tetangga["node"] not in dikunjungi:
                            biaya_tepi = tetangga["distance"]
                            tumpukan.append((tetangga["node"], jalur + [tetangga["node"]], biaya + biaya_tepi))
    
    return [], 0, len(semua_jalur)


def search_multigoal() -> tuple[list[str], int, list[str]]:
    """
    Run multigoal/destination search
    """
    path = []
    visited = 0

    if not GlobalState.malang_graph:
        console.print("[red]Data graf tidak ditemukan di GlobalState![/red]")
        return path, 0, visited

    # Get the start location
    start = GlobalState.start_location
    current_start = start
    total_biaya = 0
    semua_jalur = []

    for goal in GlobalState.destination_location:
        if GlobalState.show_process:
            console.print(f"\n[bold cyan]Searching for goal: {goal}[/bold cyan] from [green]{current_start}[/green]")

        jalur, biaya, jalur_sebagian = search(current_start, goal)
        
        if jalur:
            path.extend(jalur[1:])
            total_biaya += biaya
            semua_jalur.extend(jalur_sebagian)
            current_start = goal  # Set current goal as new start
        else:
            console.print(f"[red]Tidak ada jalur dari {current_start} ke {goal}![/red]")
            return [], 0, []

    return path, total_biaya, len(semua_jalur)

def run_dfs() -> None:
    """
    Execute the Depth First Search (DFS) algorithm.
    """
    start_time = time.time()

    # Determine if it's a single goal or multi-goal search
    if GlobalState.is_multi:
        result = search_multigoal()
    else:
        result = search()

    end_time = time.time()
    time_computation = end_time - start_time

    # Show results and calculate time
    show_result("DFS", result, time_computation)

    if GlobalState.is_multi:
        sum_distance = sum(r[1] for r in result)
    else:
        _, sum_distance, _ = result

    estimated_time = sum_distance if GlobalState.is_multi else sum_distance / 833.33  # Assume speed is 50 km/h (833.33 m/minutes)

    if estimated_time > GlobalState.max_operating_time:
        console.print(f"[bold red]WARNING!: This route takes {estimated_time:.2f} minutes, "
                      f"melebihi batas waktu operasional {GlobalState.max_operating_time} menit![/bold red]")

    if questionary.confirm("Apakah Anda ingin melihat visualisasi rute pada peta?").ask():
        visualize_route(result[0])
