from geneticAlgorithm import GeneticAlgorithm


if __name__ == "__main__":
    ga = GeneticAlgorithm(rows=11, cols=11)
    best_rule_string = ga.evolve(generations=20)
    print("Best rule string found:", best_rule_string)
