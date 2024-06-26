import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cellularAutomaton import CellularAutomaton

ABS_SIZE = 11
""" 
NASTAVENÍ PRAVIDLA
rule_string - pravidlo aplikované k vytvoření grafu
-----------------------------------------------------
RULE SETTINGS
rule_string - rule applied to create the graph
"""
rule_string = "B0567/S1248"

def run_simulation():
    live_counts = []

    initial_grid = np.zeros((ABS_SIZE, ABS_SIZE), dtype=int)
    initial_grid[ABS_SIZE // 2, ABS_SIZE // 2] = 1

    ca = CellularAutomaton(ABS_SIZE, ABS_SIZE, initial_grid)
    """ 
    ca.initialize_center_cell() - nastavení počátečního stavu na živou buňku uprostřed
    ca.randomize_grid() - nastavení počátečního stavu náhodného
    JE NUTNO ZAKOMENTOVAT TO, KTERÉ NENÍ POUŽÍVÁNO
    --------------------------------------------------------------
    ca.initialize_center_cell() - setting the initial state to the live cell in the center
    ca.randomize_grid() - set the initial state to random
    IT IS NECESSARY TO COMMENT THAT WHICH IS NOT USED
    """
    ca.initialize_center_cell()
    #ca.randomize_grid()
    
    live, _ = ca.count_live_dead()
    live_counts.append(live)

    generation = 0
    max_gen = 100
    while generation < max_gen:
        ca.apply_rules(rule_string)
        ca.grid = ca.next_grid.copy()
        live, _ = ca.count_live_dead()
        live_counts.append(live)
        generation += 1

    return live_counts

live_counts = run_simulation()

fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(live_counts, 'k-', label='Živé buňky', linewidth=2)
ax.set_xlabel('Generace')
ax.set_ylabel('Počet živých buněk')
ax.tick_params(axis='both')
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax.set_ylim(0, 121) 
plt.title('Počet živých buněk během simulace pro pravidlo ' + rule_string)
ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
ax.legend(loc='upper right')

current_directory = os.path.dirname(__file__)
file_path = os.path.join(current_directory, 'live_cells_simulation.pdf')
plt.savefig(file_path)
plt.show()
