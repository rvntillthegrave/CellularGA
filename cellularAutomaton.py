import numpy as np
import re


class CellularAutomaton:
    def __init__(self, rows, cols, initial_grid=None):
        self.rows = rows
        self.cols = cols
        if initial_grid is not None:
            self.grid = initial_grid.copy()
            self.initial_grid = initial_grid.copy()
        else:
            self.grid = np.zeros((rows, cols), dtype=int)
            self.initial_grid = np.zeros((rows, cols), dtype=int)
        self.birth_rules = []
        self.survival_rules = []

    def randomize_grid(self, probability=0.3):
        """ 
        NÁHODNÉ POČÁTEČNÍ NASTAVENÍ MŘÍŽKY
        ----------------------------------
        RANDOM INITIAL GRID SETTING
        """
        random_grid = np.random.rand(self.rows, self.cols)
        self.grid = (random_grid < probability).astype(int)
    
    def initialize_center_cell(self):
        """ 
        NASTAVENÍ POČÁTEČNÍ MŘÍŽKY NA JEDNU ŽIVOU BUŇKU UPROSTŘED
        -----------------------------------------------------------
        SETTING THE INITIAL GRID TO ONE LIVE CELL IN THE MIDDLE
        """
        self.grid = np.zeros((self.rows, self.cols), dtype=int)
        center_row = self.rows // 2
        center_col = self.cols // 2
        self.grid[center_row, center_col] = 1

    def apply_rules(self, rule_string):
        """ 
        POUŽITÍ PRAVIDEL PRO MŘÍŽKU A VYTVOŘENÍ NASTÁVÁJÍCÍ MŘÍŽKY
        -----------------------------------------------------------
        APPLYING GRID RULES AND CREATING THE RESULTING GRID
        """
        if not re.match(r'^B\d+/S\d+$', rule_string):
            raise ValueError("Invalid rule format. Expected 'Bxxx/Sxxx'.")
        b, s = rule_string.split('/')
        self.birth_rules = [int(x) for x in b[1:]]
        self.survival_rules = [int(x) for x in s[1:]]
        new_grid = np.zeros((self.rows, self.cols), dtype=int)
        for i in range(self.rows):
            for j in range(self.cols):
                neighbors = self.count_neighbors(i, j)
                if self.grid[i, j] == 0 and neighbors in self.birth_rules:
                    new_grid[i, j] = 1
                elif self.grid[i, j] == 1 and neighbors not in self.survival_rules:
                    new_grid[i, j] = 0
                else:
                    new_grid[i, j] = self.grid[i, j]
        self.next_grid = new_grid

    def count_neighbors(self, x, y):
        """ 
        VÝPOČET ŽIVÝCH BUNĚK V SOUSEDSTVÍ
        -----------------------------------
        CALCULATION OF LIVING CELLS IN THE NEIGHBOURHOOD
        """
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if self.grid[(x + i) % self.rows][(y + j) % self.cols] == 1:
                    count += 1
        return count

    def min_count_alter(self, rule_string, generations):
        """ 
        FITNESS FUNKCE - Nejmenší četnost živých buněk a zároveň alespoň jedna buňka živá
        ----------------------------------------------------------------------------------
        FITNESS FUNCTION - Least number of living cells and at least one living cell
        """
        self.randomize_grid()
        cell_count = 0
        min_living_cells = float('inf')
        generations_survived = 0

        for _ in range(generations):
            self.apply_rules(rule_string)
            living_cells = np.sum(self.grid)
            cell_count += living_cells
            if living_cells > 0:
                generations_survived += 1
                min_living_cells = min(min_living_cells, living_cells)
            
            self.grid = self.next_grid

        if generations_survived < generations:
            return 0
        else:
            return int(10000 / min_living_cells) if min_living_cells > 0 else 0

    def max_div(self, rule_string, generations):
        """ 
        FITNESS FUNKCE - Co největší rozdílnost hodnot v dvou po sobě jdoucích mřížkách
        --------------------------------------------------------------------------------
        FITNESS FUNCTION - Maximize the difference between two consecutive grids
        """
        self.randomize_grid()
        self.apply_rules(rule_string)
        prev_grid = np.copy(self.grid)
        self.grid = self.next_grid

        count_div = 0
        for gen in range(1, generations):
            self.apply_rules(rule_string)
            
            if gen >= generations - 25:
                diff_grid = np.logical_xor(self.grid, prev_grid)
                count_div += np.sum(diff_grid)
                prev_grid = np.copy(self.grid)
            
            self.grid = self.next_grid

        return int(count_div)

    def symetry_fitness(self, rule_string, generations):
        """ 
        FITNESS FUNKCE - Symetrie a zajímavé vzory
        -------------------------------------------
        FITNESS FUNCTION - Symmetry and interesting patterns
        """
        self.initialize_center_cell()

        complexity_score = 0
        pattern_score = 0
        density_score = 0
        diversity_score = 0
        penalty = 0

        prev_grid = self.grid.copy()
        previous_states = set()

        for gen in range(generations):
            self.apply_rules(rule_string)

            current_state = self.grid.tostring()
            if current_state in previous_states:
                penalty += 50
            previous_states.add(current_state)

            complexity_score += np.sum(np.abs(self.grid - prev_grid))

            pattern_score += (self.rows * self.cols - np.sum(np.abs(self.grid - np.fliplr(self.grid))) - np.sum(np.abs(self.grid - np.flipud(self.grid)))) / (self.rows * self.cols)

            density_score += np.sum(self.grid) / (self.rows * self.cols)
            diversity_score += len(set(self.grid.flatten()))

            prev_grid = self.grid.copy()
            self.grid = self.next_grid

        total_score = complexity_score + pattern_score + density_score * diversity_score - penalty
        return max(0, int(total_score / (10 + 0.1 * (self.rows - 11) ** 2)))
        
    def alternating_pattern(self, rule_string, generations):
        """ 
        FITNESS FUNKCE - Šachovnicový vzor
        ----------------------------------------
        FITNESS FUNCTION - Checkerboard pattern
        """
        self.initialize_center_cell()
        pattern_score = 0

        for gen in range(generations):
            self.apply_rules(rule_string)
            self.grid = self.next_grid.copy()

            if gen >= generations - 20:
                checkerboard1 = np.indices((self.rows, self.cols)).sum(axis=0) % 2
                checkerboard2 = 1 - checkerboard1

                match1 = np.sum(self.grid == checkerboard1)
                match2 = np.sum(self.grid == checkerboard2)

                pattern_score = max(match1, match2) / (self.rows * self.cols)

        return (pattern_score - 0.5)*100        