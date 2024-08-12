from functools import partial
import deap
import SQLCostCalculator
import random
from deap import creator, base, tools
from SQLCostCalculator import evaluate

# function that creates an individual as a permutation of a range of numbers
def create_permutation(size):
    return random.sample(range(size), size)

# Convert the permutation back to the original sequence
def convert_permutation_to_original(individual, original_sequence):
    return [original_sequence[i] for i in individual]

#function for partially matched crossover
def part_matched_cx(ind1, ind2):

    #print("TESTING", ind1, "STILL TESTING:  ", ind2)
    size = len(ind1)
    p1, p2 = {}, {}

    # Initialize the position of each index in the individuals
    for i in range(size):
        p1[ind1[i]] = i
        p2[ind2[i]] = i

    # Choose crossover points
    cxpoint1, cxpoint2 = sorted(random.sample(range(size), 2))

    # Apply crossover between cx points
    for i in range(cxpoint1, cxpoint2):
        # Swap the matched value
        temp1 = ind1[i]
        temp2 = ind2[i]
        ind1[i], ind1[p1[temp2]] = temp2, temp1
        ind2[i], ind2[p2[temp1]] = temp1, temp2

        # Position bookkeeping
        p1[temp1], p1[temp2] = p1[temp2], p1[temp1]
        p2[temp1], p2[temp2] = p2[temp2], p2[temp1]

    return ind1, ind2 

#function for swap mutation
def swapmut(individual, indpb):
    """Mutate an individual by swapping two of its attributes."""
    size = len(individual)
    for i in range(size):
        if random.random() < indpb:
            swap_idx = random.randrange(size)
            # Swap the elements
            individual[i], individual[swap_idx] = individual[swap_idx], individual[i]
    return individual,

def evaluate(sequence, join_stats, original_sequence):
    joins = convert_permutation_to_original(sequence, original_sequence)
    return SQLCostCalculator.evaluate(joins, join_stats)


def genetic_algorithm(joins, join_stats):

    # DEAP setup
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)  

    toolbox = base.Toolbox()
    toolbox.register("indices", create_permutation, len(joins))
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", partial(evaluate, join_stats=join_stats, original_sequence=joins))
    toolbox.register("mate", part_matched_cx)
    toolbox.register("mutate", swapmut)
    toolbox.register("select", tools.selTournament, tournsize=3)

    population = toolbox.population(n=100)
    ngen = 40
    cxpb = 0.8
    mutpb = 0.4
    elitism_size = 5 

    for gen in range(ngen):

        #print("Generation: ", gen)
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

            toolbox.mutate(offspring, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = list(map(toolbox.evaluate, invalid_ind))
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the best individuals to be preserved
        elites = tools.selBest(population, elitism_size)
        # Replace the worst individuals with the best from the previous generation
        offspring.extend(elites)

        # The population is entirely replaced by the offspring + elites
        population[:] = offspring

    del creator.Individual
    del creator.FitnessMin

    # Print the best solution
    best_ind = tools.selBest(population, 1)[0]
    best_seq = convert_permutation_to_original(best_ind, joins)
    print(f"Optimal Join Order: {best_seq}")
    print(f"Cost: {evaluate(best_ind, join_stats, joins)[0]}")