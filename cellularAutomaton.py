import numpy as np
import re
import scipy
import scipy.ndimage


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

    def get_initial_state(self):
        return self.initial_grid.copy()

    def randomize_grid(self, probability=0.3):
        random_grid = np.random.rand(self.rows, self.cols)
        self.grid = (random_grid < probability).astype(int)

    def apply_rules(self, rule_string):
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
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if self.grid[(x + i) % self.rows][(y + j) % self.cols] == 1:
                    count += 1
        return count

    def get_current_state(self):
        return self.grid

    def get_next_state(self):
        return self.next_grid

    def max_count(self, rule_string, generations):
        self.randomize_grid()
        total_living_cells = 0

        for _ in range(generations):
            self.apply_rules(rule_string)
            total_living_cells += np.sum(self.grid)
            self.grid = self.next_grid

        return int(total_living_cells)

    def min_count(self, rule_string, generations):
        self.randomize_grid()
        total_living_cells = 0

        for _ in range(generations):
            self.apply_rules(rule_string)
            total_living_cells += np.sum(self.grid)
            self.grid = self.next_grid

        return int(1000 / total_living_cells)

    def min_count_alter(self, rule_string, generations):
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
        self.randomize_grid()
        self.apply_rules(rule_string)
        prev_grid = np.copy(self.grid)
        self.grid = self.next_grid

        count_div = 0
        for _ in range(1, generations):
            self.apply_rules(rule_string)
            diff_grid = np.logical_xor(self.grid, prev_grid)
            count_div += np.sum(diff_grid)
            prev_grid = np.copy(self.grid)
            self.grid = self.next_grid

        return int(count_div)

    def carpet_fitness(self, rule_string, generations):
        self.grid = np.zeros((self.rows, self.cols), dtype=int)
        self.grid[self.rows // 2, self.cols // 2] = 1

        local_structure = 0
        exploration = 0
        complexity = 0

        prev_grid = self.grid.copy()

        for _ in range(generations):
            self.apply_rules(rule_string)

            local_structure += np.sum(self.grid * scipy.ndimage.uniform_filter(self.grid, size=3))
            exploration += np.sum(np.abs(self.grid - prev_grid))
            complexity += np.sum(np.abs(self.grid - np.roll(self.grid, 1, axis=0))) + 1

            prev_grid = self.grid.copy()
            self.grid = self.next_grid

        fitness = (local_structure / (self.rows * self.cols * generations)) * (exploration / generations) * (complexity / generations)
        return int(fitness)

    def carpet_fitness_alter(self, rule_string, generations):
        self.grid = np.zeros((self.rows, self.cols), dtype=int)
        self.grid[self.rows // 2, self.cols // 2] = 1

        symmetry = 0
        complexity = 0
        pattern_score = 0
        density = 0

        prev_grid = self.grid.copy()

        for _ in range(generations):
            self.apply_rules(rule_string)
            symmetry += np.sum(np.abs(self.grid - np.fliplr(self.grid))) + np.sum(np.abs(self.grid - np.flipud(self.grid)))
            complexity += np.sum(np.abs(self.grid - prev_grid))

            for i in range(self.rows):
                for j in range(self.cols):
                    if self.grid[i, j] == 1:
                        if i < self.rows // 2:
                            if self.grid[self.rows - i - 1, j] == 1:
                                pattern_score += 1
                        if j < self.cols // 2:
                            if self.grid[i, self.cols - j - 1] == 1:
                                pattern_score += 1
                        if i < self.rows // 2 and j < self.cols // 2:
                            if self.grid[self.rows - i - 1, self.cols - j - 1] == 1:
                                pattern_score += 1
            density += np.sum(self.grid) / (self.rows * self.cols)
            prev_grid = self.grid.copy()
            self.grid = self.next_grid

        fitness = complexity * pattern_score * density / (symmetry + 1)
        return int(fitness / 100000)
