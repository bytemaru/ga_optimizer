import sys
import SQLParser 
import SQLGenAlg
import SQLCostCalculator
import validate
from SQLParser import parse_sql
from SQLGenAlg import genetic_algorithm
from SQLCostCalculator import read_join_stats_from_excel
from validate import calculate_all_permutations_cost

def main():
    SQLfilename = sys.argv[1]
    join_selectivity_file = sys.argv[2]

    #load table sizes and join selectivities
    read_join_stats_from_excel(join_selectivity_file)

    #parse SQL file
    SQLJoins = parse_sql(SQLfilename)

    #run GA on joins
    genetic_algorithm(SQLJoins)

    #validate GA result
    best, cost = calculate_all_permutations_cost(SQLJoins["FROM"])
    print("Real Optimal Join Order: ", best)
    print("Optimal Cost: ", cost)


if __name__ == "__main__":
    main()