import sys
import os
from SQLParser import parse_sql
from SQLGenAlg import genetic_algorithm
from SQLCostCalculator import JoinStats
from validate import calculate_all_permutations_cost

def main():
    SQLfilepath = sys.argv[1]
    join_selectivity_file = sys.argv[2]

    result_file = open("output.txt", "w")

    dir_list = os.listdir(SQLfilepath)
    SQLfiles = []
    for f in dir_list:
        abs_file_path = os.path.join(SQLfilepath, f)
        SQLfiles.append(abs_file_path)

    #load table sizes and join selectivities
    join_stats = JoinStats(join_selectivity_file)

    for f in SQLfiles: 
        result_file.write("Query: %s\n" % f)
        #parse SQL file
        SQLJoins = parse_sql(f)
        joins = SQLJoins["FROM"]
        joins.append('?')
        joins.append('?')
        for i in range(30):
            result_file.write("Iteration: %d \n" % i)
            #run GA on joins
            print(joins)
            result_file.write(genetic_algorithm(joins, join_stats))
        
        #validate GA result
        # best, cost = calculate_all_permutations_cost(SQLJoins["FROM"], join_stats)
        # result_file.write("Best Join Order: %s" % best)
        # result_file.write("Optimal Cost: %s" % cost)

    result_file.close()

if __name__ == "__main__":
    main()