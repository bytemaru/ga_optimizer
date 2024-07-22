import sys
import os
from SQLParser import parse_sql
from SQLGenAlg import genetic_algorithm
from SQLCostCalculator import read_join_stats_from_excel
from validate import calculate_all_permutations_cost

def main():
    SQLfilepath = sys.argv[1]
    join_selectivity_file = sys.argv[2]

    dir_list = os.listdir(SQLfilepath)
    print("Files and directories in '", SQLfilepath, "' :")
    # prints all files
    print(dir_list)

    #load table sizes and join selectivities
    read_join_stats_from_excel(join_selectivity_file)

    for f in dir_list: 
        print(f)
        #parse SQL file
        SQLJoins = parse_sql(f)

        #run GA on joins
        genetic_algorithm(SQLJoins)

        #validate GA result
        best, cost = calculate_all_permutations_cost(SQLJoins["FROM"])
        print("Best Join Order: ", best)
        print("Optimal Cost: ", cost)

if __name__ == "__main__":
    main()