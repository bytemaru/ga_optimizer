import pandas as pd

join_stats = {}

def read_join_stats_from_excel(file_path):
    df = pd.read_excel(file_path, header=None, usecols=[0, 1, 2, 3, 4])
    df.columns = ['table1_name', 'table2_name', 'table1_size', 'table2_size', 'selectivity']
    for _, row in df.iterrows():
        table1 = row['table1_name']
        table2 = row['table2_name']
        size1 = row['table1_size']
        size2 = row['table2_size']
        selectivity = row['selectivity']
        cost = (size1 + size2) * selectivity
        join_stats[(table1, table2)] = cost
        join_stats[(table2, table1)] = cost  # Assuming join cost is symmetric

# Fitness function to calculate the cost of a join order
def evaluate(individual):
    cost = 0
    for i in range(1, len(individual)):
        cost += join_stats.get((individual[i-1], individual[i]), float(1))
    return (cost,)