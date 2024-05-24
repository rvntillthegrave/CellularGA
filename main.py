from geneticAlgorithm import GeneticAlgorithm
import time

if __name__ == "__main__":
    """ 
        ROMĚRY MŘÍŽKY CELULÁRNÍHO AUTOMATU 
        rows - POČET BUNĚK V ŘÁDKU
        cols - POČET BUNĚK V SLOUPCI
        -----------------------------
        DIMENSIONS OF THE CELLULAR AUTOMATON GRID
        rows - NUMBER OF CELLS IN A ROW
        cols - NUMBER OF CELLS IN A COLUMN
        
        VELIKOST POPULACE
        population_size - VELIKOST POPULACE PRAVIDEL V JEDNÉ GENERACI GENETICKÉHO ALGORITMU
        ------------------------------------------------------------------------------------
        POPULATION SIZE
        population_size - POPULATION SIZE OF RULES IN ONE GENERATION OF THE GENETIC ALGORTIHM
        
        MUTACE
        mutation_rate - PRAVDĚPODOBNOST MUTACE CHROMOZOMU (0.1 = 1 %)
        -------------------------------------------------------------
        MUTATION
        mutation_rate - CHROMOSOME MUTATION RATE (0.1 = 1%)
        
        DÉLKA SIMULACE PRAVIDLA PRO CELULÁRNÍ AUTOMAT
        cagens - POČET GENERACÍ, PO KTERÉ BUDE CELULÁRNÍ AUTOMAT S JEDNOTLIVÝM PRAVIDLEM SIMULOVÁN
        -----------------------------------------------------------------------------------------------
        SIMULATION LENGTH FOR CELLULAR AUTOMATON WITH DEFINED RULE
        cagens - NUMBER OF GENERATIONS FOR WHICH A CELLULAR AUTOMATON WITH A UNIFIED RULE WILL BE SIMULATED

        SELEKCE
        PRO SELEKCI TURNAJOVOU NASTAVIT DO PROMĚNNÉ selection = 't'
        PRO SELEKCI RULETOVÝM KOLEM NASTAVIT DO PROMĚNNÉ selection = 'r'
        --------------------------------------------------------
        SELECTION
        FOR TOURNAMENT SELECTION SET VARIABLE selection = 't'
        FOR ROULLETTE WHEEL SELECTION SET VARIABLE selection = 'r'
        
        FITNESS FUNKCE
        'min' - CO NEJMENŠÍ ČETNOST ŽIVÝCH BUNĚK NA MŘÍŽCE V PRŮBĚHU SIMULACE 
                                 \A ZÁROVEŇ ALEPSOŇ JEDNA ŽIVÁ PŘI KAŽDÉ GENRACI
        'div' - CO NEJVĚTŠÍ ROZDÍL MEZI DVĚMI PO SOBĚ JDOUCÍMI MŘÍŽKAMI
        'sym' - ZAJÍMAVÉ VZORY A SYMETRIE
        'alt' - ŠACHOVNICOVÝ VZOR
        ------------------------------------------------------------------------------------
        FITNESS FUNCTIONS
        'min' - THE LOWEST NUMBER OF LIVE CELLS ON THE GRID DURING THE SIMULATION 
                                 \AND AT LEAST ONE LIVE CELL AT EACH GENERATION
        'div' - THE LARGEST DIFFERENCE BETWEEN TWO CONSECUTIVE GRIDS
        'sym' - INTERESTING PATTERNS AND SYMMETRIES
        'alt' - CHECKERBOARD PATTERN
        
        DÉLKA GENETICKÉHO ALGORITMU
        generations - POČET GENERACÍ GENETICKÉHO ALGORITMU, PO KTERÉM SE SMYČKA UZAVŘE //
                        A VYHODNOTÍ ČLEN S NEJVYŠŠÍ FINTESS
        -----------------------------
        LENGTH OF THE GENETIC ALGORITHM
        generations - THE NUMBER OF GENERATIONS OF THE GENETIC ALGORITHM AFTER WHICH THE LOOP//
                        IS CLOSED AND THE MEMBER WITH THE HIGHEST FINTESS IS EVALUATED
    """
    start_time = time.time()
    ga = GeneticAlgorithm(rows=9, cols=9, population_size=150, 
                          mutation_rate=0.01, cagens=100, selection="t", fitfun="alt")
    best_rule_string = ga.evolve(generations=30)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Best rule string found:", best_rule_string, "in", int(elapsed_time), "seconds")