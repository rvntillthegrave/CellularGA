import random
from concurrent.futures import ThreadPoolExecutor
import operator
import numpy as np 
from cellularAutomaton import CellularAutomaton


class GeneticAlgorithm:
    def __init__(self, rows, cols, population_size, mutation_rate, cagens, selection, fitfun):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.gens = cagens
        self.selection = selection
        self.fitfun = fitfun
        self.population = [self.generate_rule_string() for _ in range(population_size)]
        self.ca = CellularAutomaton(rows, cols)

    def check_rule(self, rule):
        """ 
        KONTROLA SPRÁVNOSTI FORMÁTU PRAVIDEL
        ------------------------------------
        CHECKS THE CORRECTNESS OF THE RULES
        """
        b, s = rule.split('/')
        sorted_b = ''.join(sorted(set(b)))
        sorted_s = ''.join(sorted(set(s)))
        return b == sorted_b and s == sorted_s
    
    def sort_and_remove_duplicates(self, rule):
        """ 
        ODSTRANĚNÍ DUPLIKÁTNÍCH ČÍSEL V PRAVIDLECH A SEŘAZENÍ
        -----------------------------------------------------
        REMOVES DUPLICATE NUMBERS IN THE RULES AND SORTS THEM
        """
        b, s = rule.split('/')
        b = b[1:]
        s = s[1:]
        sorted_b = ''.join(sorted(set(b)))
        sorted_s = ''.join(sorted(set(s)))
        return f"B{sorted_b}/S{sorted_s}"

    def generate_rule_string(self):
        """ 
        VYTVOŘENÍ POČÁTEČNÍHO NÁHODNÉHO PRAVIDLA
        ----------------------------------------
        CREATES AN INITIAL RANDOM RULE
        """
        b_conditions = ''.join(sorted(random.sample(['0', '1', '2', '3', '4', '5', '6', '7', '8'], random.randint(1, 8))))
        s_conditions = ''.join(sorted(random.sample(['0', '1', '2', '3', '4', '5', '6', '7', '8'], random.randint(1, 8))))
        return f'B{b_conditions}/S{s_conditions}'
    
    def simulate_rule(self, rule_string):
        """ 
        SIMULACE CELULÁRNÍHO AUTOMATU
        
        local_ca.min_count_alter - CO NEJMENŠÍ ČETNOST ŽIVÝCH BUNĚK NA MŘÍŽCE V PRŮBĚHU SIMULACE 
                                 \A ZÁROVEŇ ALEPSOŇ JEDNA ŽIVÁ PŘI KAŽDÉ GENRACI
        local_ca.max_div - CO NEJVĚTŠÍ ROZDÍL MEZI DVĚMI PO SOBĚ JDOUCÍMI MŘÍŽKAMI
        local_ca.symetry_fitness - ZAJÍMAVÉ VZORY A SYMETRIE
        local_ca.alternating_pattern - ŠACHOVNICOVÝ VZOR
        ------------------------------------------------------------------------------------
        SIMULATES A CELLULAR AUTOMATON
        
        local_ca.min_count_alter - THE LOWEST NUMBER OF LIVE CELLS ON THE GRID DURING THE SIMULATION 
                                 \AND AT LEAST ONE LIVE CELL AT EACH GENERATION
        local_ca.max_div - THE LARGEST DIFFERENCE BETWEEN TWO CONSECUTIVE GRIDS
        local_ca.symetry_fitness - INTERESTING PATTERNS AND SYMMETRIES
        local_ca.alternating_pattern - CHECKERBOARD PATTERN
        """
        local_ca = CellularAutomaton(self.ca.rows, self.ca.cols)
        if self.fitfun == "min":
            return local_ca.min_count_alter(rule_string, self.gens)
        elif self.fitfun == "div":
            return local_ca.max_div(rule_string, self.gens)
        elif self.fitfun == "sym":
            return local_ca.symetry_fitness(rule_string, self.gens)
        elif self.fitfun == "alt":
            return local_ca.alternating_pattern(rule_string, self.gens)
        else:
            print("NEPLATNÉ NASTAVENÍ FITNESS FUNKCE")
    
    def evaluate_fitness(self):
        """ 
        URČENÍ FITNESS HODNOTY PRO KAŽDÉHO JEDINCE Z GENERACE
        ------------------------------------------------------
        DETERMINES FITNESS VALUES FOR EACH INDIVIDUAL IN THE GENERATION
        """
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = []
            for rule_string in self.population:
                future = executor.submit(self.simulate_rule, rule_string)
                fitness_value = future.result()
                print(fitness_value, "  (", rule_string,")")
                results.append((fitness_value, rule_string))
        return results

    def select_parents(self, fitness_values, tournament_size=2):
        """ 
        VÝBĚR DVOU RODIČŮ PRO KŘÍŽENÍ (METODA VÁŽENÉ RULETY NEBO TURNAJE)
        PRO SELEKCI TURNAJOVOU NASTAVIT DO PROMĚNNÉ selection = 't'
        PRO SELEKCI VÁŽENOU RULETOU NASTAVIT DO PROMĚNNÉ selection = 'r'
        ------------------------------------------------------------------
        SELECTS TWO PARENTS FOR CROSSBREEDING (WEIGHTED ROULETTE OR TOURNAMENT SELECTION)
        FOR TOURNAMENT SELECTION SET VARIABLE selection = 't'
        FOR TOURNAMENT SELECTION SET VARIABLE selection = 'r'
        """
        if self.selection == "t":
            return self.tournament_selection(fitness_values, tournament_size)
        elif self.selection == "r":
            return self.roulette_selection(fitness_values)

    def tournament_selection(self, fitness_values, tournament_size):
        """ 
        TURNAJOVA SELEKCE
        """
        def tournament():
            participants = random.sample(fitness_values, tournament_size)
            winner = max(participants, key=lambda participant: participant[0])
            return winner

        parent1 = tournament()
        parent2 = tournament()
        while parent1 == parent2: 
            parent2 = tournament()
        return [parent1, parent2]

    def roulette_selection(self, fitness_values):
        """ 
        SELEKCE VAZENOU RULETOU
        """
        total_fitness = sum(fitness for fitness, _ in fitness_values)
        probabilities = [fitness / total_fitness for fitness, _ in fitness_values]
        return random.choices(fitness_values, weights=probabilities, k=2)

    def crossover(self, parent1, parent2):
        """ 
        PROCES KŘÍŽENÍ DVOU RODIČŮ A TVORBA DVOU POTOMKŮ (PRAVIDLO JE ROZDĚLENO NA DVĚ ČÁSTI A TY JSOU NÁSLEDNĚ JEDNOBODOVĚ KŘÍŽENY)
        NÁSLEDNĚ JE PROVEDENA KONTROLA SPRÁVNOSTI FORMÁTU NOVĚ VZNIKLÝCH PRAVIDEL, PŘÍPADNÁ OPRAVA
        -------------------------------------------------------------------------------------------
        THE PROCESS OF CROSSBREEDING OF TWO PARENTS AND CREATING TWO OFFSPRING (THE RULE IS DIVIDED INTO TWO PARTS AND THEY ARE SUBSEQUENTLY 
        CROSSED AT ONE POINT) THEN THE CORRECTNESS OF THE FORMAT OF THE NEWLY CREATED RULES IS CHECKED, POSSIBLE CORRECTION IS DONE IF NEEDED
        """
        b1, s1 = parent1.split('/')
        b2, s2 = parent2.split('/')
        b1, b2 = b1[1:], b2[1:]
        s1, s2 = s1[1:], s2[1:]

        child1_b = b1[:len(b1)//2] + b2[len(b2)//2:]
        child1_s = s1[:len(s1)//2] + s2[len(s2)//2:]
        child2_b = b2[:len(b2)//2] + b1[len(b1)//2:]
        child2_s = s2[:len(s2)//2] + s1[len(s1)//2:]
        
        child1 = f'B{child1_b}/S{child1_s}'
        child2 = f'B{child2_b}/S{child2_s}'
        
        if not self.check_rule(child1):
            child1 = self.sort_and_remove_duplicates(child1)
        if not self.check_rule(child2):
            child2 = self.sort_and_remove_duplicates(child2)
        return child1, child2

    def mutate(self, individual):
        """
        OPERÁTOR MUTACE - POKUD JE NÁHODNĚ VYBRANÉ ČÍSLO MENŠÍ NEŽ self.mutation_rate, DOCHÁZÍ K MUTACI GENU.
        -------------------------------------------------------------------------------------------------------
        MUTATION OPERATOR - IF A RANDOMLY SELECTED NUMBER IS LESS THAN self.mutation_rate, A GENE IS MUTATED.
        """
        if random.random() < self.mutation_rate:
            b, s = individual.split('/')
            b_numbers = b[1:]
            s_numbers = s[1:]

            if random.random() < 0.5:
                target_list = list(b_numbers)
                part = 'B'
            else:
                target_list = list(s_numbers)
                part = 'S'

            available_positions = [i for i in range(len(target_list))]

            if not available_positions:
                return individual

            selected_position = random.choice(available_positions)
            existing_genes = set(target_list)
            new_gene = str(random.randint(0, 8))

            while new_gene in existing_genes:
                new_gene = str(random.randint(0, 8))

            target_list[selected_position] = new_gene

            if part == 'B':
                mutated_individual = f'B{"".join(target_list)}/S{s_numbers}'
            else:
                mutated_individual = f'B{b_numbers}/S{"".join(target_list)}'


            return self.sort_and_remove_duplicates(mutated_individual)
        else:
            return self.sort_and_remove_duplicates(individual)
  
    def evolve(self, generations):
        """ 
        PROCES EVOLUCE - URČENÍ FITNESS HODNOTY, SELEKCE RODIČOVSÝCH PRAVIDEL, PROCES KŘÍŽENÍ, MUTACE.
        V GENERACI JE VŽDY VYBRÁN JEDINEC S NEVYŠŠÍ HODNOTOU FITNESS - TEN NENÍ PODROBEN KŘÍŽENÍ A MUTACI
        A PŘECHÁZÍ ROVNOU DO NOVÉ GENERACE, KDE NAHRADÍ NEJHORŠÍHO JEDINCE (ELITISMUS)
        ---------------------------------------------------------------------------------
        PROCESS OF EVOLUTION - DETERMINATION OF FITNESS VALUE, SELECTION OF PARENTAL RULES, PROCESS OF 
        CROSSOVER AND MUTATION. IN A GENERATION THE INDIVIDUAL WITH THE HIGHEST FITNESS VALUE IS NOT SUBJECTED 
        TO CROSSOVER AND MUTATION AND IS PASSED DIRECTLY TO THE NEW GENERATION, WHERE IT REPLACES 
        THE WORST INDIVIDUAL (ELITISM)
        """
        for gen in range(generations):
            print("_____________________ GENERACE:", gen+1, "_____________________")
            fitness_values = self.evaluate_fitness()
            new_population = []
            for _ in range(self.population_size-1):
                parents = self.select_parents(fitness_values)
                parent1_rule = parents[0][1]
                parent2_rule = parents[1][1]
                child1, child2 = self.crossover(parent1_rule, parent2_rule)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.extend([child1, child2])
            gen_rule = max(fitness_values, key=operator.itemgetter(0))[1]
            worst_fitness_idx = min(range(len(fitness_values)), key=lambda i: fitness_values[i][0])
            new_population[worst_fitness_idx] = gen_rule
            self.population = new_population
        best_rule_string = gen_rule
        return best_rule_string