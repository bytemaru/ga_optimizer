import deap
import SQLCostCalculator
import random
from deap import creator, base, algorithms, tools
from SQLCostCalculator import evaluate

def genetic_algorithm(joins):
    
    tables = list(joins["FROM"])
    print(tables)

    # DEAP setup
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("indices", random.sample, tables, len(tables))
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    population = toolbox.population(n=100)
    ngen = 40
    cxpb = 0.8
    mutpb = 0.2
    elitism_size = 5 

    for gen in range(ngen):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population) - elitism_size)
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the best individuals to be preserved
        elites = tools.selBest(population, elitism_size)
        # Replace the worst individuals with the best from the previous generation
        offspring.extend(elites)

        # The population is entirely replaced by the offspring + elites
        population[:] = offspring

    # Print the best solution
    best_ind = tools.selBest(population, 1)[0]
    print(f"Optimal Join Order: {best_ind}")
    print(f"Cost: {evaluate(best_ind)[0]}")