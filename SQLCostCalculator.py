import pandas as pd

#join_stats = pd.DataFrame()

def read_join_stats_from_excel(file_path):
    join_stats = pd.read_excel(file_path, header=None, usecols=[0, 1, 2, 3, 4])
    join_stats.columns = ['table1_name', 'table2_name', 'table1_size', 'table2_size', 'selectivity']
    join_stats.columns = join_stats.columns.str.strip()
    join_stats[['table1_name', 'table2_name']] = join_stats[['table1_name', 'table2_name']].astype(str)
    join_stats[['table1_size', 'table2_size', 'selectivity']] = join_stats[['table1_size', 'table2_size', 'selectivity']].astype('float64')
    bruh = "movie_companies"
    print("Presence Check: ", join_stats['table1_name'].str.contains(bruh).any())

    return join_stats

def calculate_join_cost(join1, join2, join_stats): 

    cost = 0

    try:
        # Attempt to get size1 from table1
        size1 = join_stats.loc[join_stats['table1_name'] == join1, 'table1_size']
        if size1.empty:
            # If not found in table1, attempt to get from table2
            size1 = join_stats.loc[join_stats['table2_name'] == join1, 'table2_size']
        if not size1.empty:
            size1 = size1.dropna().iloc[0]
    except KeyError as e:
        #print(f"Column not found: {e}", "ERROR: ", join1)
        size1 = pd.Series(dtype='float64')  # Return empty Series if KeyError occurs
        
    try:
        # Attempt to get size1 from table1
        size2 = join_stats.loc[join_stats['table1_name'] == join2, 'table1_size']
        if size2.empty:
            # If not found in table1, attempt to get from table2
            size2 = join_stats.loc[join_stats['table2_name'] == join2, 'table2_size']
        if not size2.empty:
            size2 = size2.dropna().iloc[0]
    except KeyError as e:
        #print(f"Column not found: {e}")
        size2 = pd.Series(dtype='float64')  # Return empty Series if KeyError occurs

    try:
        # Attempt to get size1 from table1
        selectivity = join_stats.loc[(join_stats['table1_name'] == join1) & (join_stats['table2_name'] == join2), 'selectivity']
        if selectivity.empty:
            # If not found in table1, attempt to get from table2
            selectivity = join_stats.loc[(join_stats['table1_name'] == join2) & (join_stats['table2_name'] == join1), 'selectivity']
        if selectivity.empty:
            selectivity = 1.0
        else:
            # Handle NaN values if needed
            selectivity = selectivity.dropna().iloc[0] if not selectivity.dropna().empty else 1.0
    except KeyError as e:
        selectivity = 1 # Selecticity = 1 if no join is found - KeyError occurs
    
    cost = (size1 + size2) * float(selectivity)
    return cost


# Fitness function to calculate the cost of a join order
def evaluate(individual, join_stats):
    cost = 0
    for i in range(1, len(individual)):
        cost += calculate_join_cost(str(individual[i-1]), str(individual[i]), join_stats)
    return (float(cost),)