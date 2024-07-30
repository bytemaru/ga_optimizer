import itertools
import SQLCostCalculator
from SQLCostCalculator import evaluate

# Function to calculate the cost of every possible permutation
def calculate_all_permutations_cost(strings, join_stats):
    # Generate all possible permutations
    all_permutations = itertools.permutations(strings)
    
    min_cost = float('inf')
    best_permutation = None

    # Iterate over all permutations and calculate their cost
    for perm in all_permutations:
        cost = evaluate(perm, join_stats)[0]  # Evaluate returns a tuple, so take the first element
        if cost < min_cost:
            min_cost = cost
            best_permutation = perm

    return best_permutation, min_cost