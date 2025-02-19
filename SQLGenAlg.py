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


# Initialize stagnation counter as a global variable
stagnation_counter = 0
prev_best_fitness = float('inf')

def adaptive_crossover_rate(gen, max_gen, prev_best_fitness, current_best_fitness,
                            base_rate=0.9, min_rate=0.4, stagnation_boost=0.1, patience=5):
    """
    Adapt crossover rate based on:
    - Generation progress (linear decay)
    - Stagnation detection (if no improvement for 'patience' generations)

    Returns: Updated crossover probability.
    """
    global stagnation_counter

    # Linear decay
    crossover_rate = base_rate - (base_rate - min_rate) * (gen / max_gen)

    # Detect stagnation (if best fitness hasn't improved)
    if current_best_fitness >= prev_best_fitness:
        stagnation_counter += 1
    else:
        stagnation_counter = 0  # Reset counter if improvement occurs

    # If stagnation persists, increase crossover rate slightly
    if stagnation_counter >= patience:
        crossover_rate = min(0.9, crossover_rate + stagnation_boost)
        stagnation_counter = 0  # Reset counter after adjustment

    return crossover_rate


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

    global prev_best_fitness

    population = toolbox.population(n=100)
    ngen = 40
    cxpb = 0.9
    mutpb = 0.4
    elitism_size = 5

    convergence_data = []

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

            if random.random() < mutpb:
                toolbox.mutate(offspring, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = list(map(toolbox.evaluate, invalid_ind))
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = (fit, )

        # Select the best individuals to be preserved
        elites = tools.selBest(population, elitism_size)
        # Replace the worst individuals with the best from the previous generation
        offspring.extend(elites)

        # The population is entirely replaced by the offspring + elites
        population[:] = offspring

        # Store best fitness for convergence curve
        best_sample = tools.selBest(population, 1)[0]
        best_sample_cost = evaluate(best_sample, join_stats, joins)
        convergence_data.append(best_sample_cost)

        # Update mutation rate
        cxpb = adaptive_crossover_rate(gen, ngen, prev_best_fitness, best_sample_cost)

        prev_best_fitness = best_sample_cost

    del creator.Individual
    del creator.FitnessMin

    # Print the best solution
    best_ind = tools.selBest(population, 1)[0]
    best_seq = convert_permutation_to_original(best_ind, joins)
    result = (f"Optimal Join Order: {best_seq} \n")
    result += (f"Cost: {evaluate(best_ind, join_stats, joins)} \n")
    result += (f"Convergence curve: {convergence_data} \n")
    return result