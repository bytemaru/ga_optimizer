import pandas as pd

import pandas as pd

class JoinStats:
    def __init__(self, file_path):
        self._join_stats = self._read_join_stats_from_excel(file_path)

    @property
    def join_stats(self):
        return self._join_stats

    def _read_join_stats_from_excel(self, file_path):
        join_stats = pd.read_excel(file_path, header=None, usecols=[0, 1, 2, 3, 4])
        join_stats.columns = ['table1_name', 'table2_name', 'table1_size', 'table2_size', 'selectivity']
        join_stats.columns = join_stats.columns.str.strip()
        join_stats[['table1_name', 'table2_name']] = join_stats[['table1_name', 'table2_name']].astype(str)
        join_stats[['table1_size', 'table2_size', 'selectivity']] = join_stats[['table1_size', 'table2_size', 'selectivity']].astype('float64')
        
        return join_stats
    
    def get_size(self, table): 
        try:
            # Attempt to get size1 from table1
            size = self._join_stats.loc[self._join_stats['table1_name'] == table, 'table1_size']
            if size.empty:
                # If not found in table1, attempt to get from table2
                size = self._join_stats.loc[self._join_stats['table2_name'] == table, 'table2_size']
            if not size.empty:
                size = size.dropna().iloc[0]
                return size
        except KeyError as e:
            #print(f"Column not found: {e}", "ERROR: ", join1)
            size = pd.Series(dtype='float64')  # Return empty Series if KeyError occurs

    def get_selectivity(self, join1, join2): 
        try:
            # Attempt to get selectivity with join1, join2
            selectivity = self._join_stats.loc[(self._join_stats['table1_name'] == join1) & (self._join_stats['table2_name'] == join2), 'selectivity']
            if selectivity.empty:
                # If not found in table1, attempt to get selectivity with join2, join1
                selectivity = self._join_stats.loc[(self._join_stats['table1_name'] == join2) & (self._join_stats['table2_name'] == join1), 'selectivity']
            if selectivity.empty:
                selectivity = 1.0
            else:
                # Handle NaN values if needed
                selectivity = selectivity.dropna().iloc[0] if not selectivity.dropna().empty else 1.0
            return selectivity
        except KeyError as e:
            selectivity = 1 # Selecticity = 1 if no join is found - KeyError occurs

def get_lowest_selectivity(left_set, right_set, join_stats): 
    best_selectivity = 1.0
    for left in left_set: 
        for right in right_set: 
            selectivity = join_stats.get_selectivity(left, right)
            if selectivity < best_selectivity: 
                best_selectivity = selectivity
    return best_selectivity

def calculate_sequence_cost(joins, join_stats): 
    cost = 0
    explored_joins = []

    if len(joins) == 1:
        return join_stats.get_size(joins[0])

    for i in range(len(joins)):
        if not explored_joins:
            cost += (join_stats.get_size(joins[i]) + join_stats.get_size(joins[i+1])) * join_stats.get_selectivity(joins[i], joins[i+1])
            explored_joins.append(joins[i])
            explored_joins.append(joins[i+1])
        else: 
            min_selectivity = 1.0
            min_size = ''
            for expl_join in explored_joins: 
                selectivity = join_stats.get_selectivity(joins[i], expl_join)
                if selectivity <= min_selectivity: 
                    min_selectivity = selectivity
                    min_size = expl_join
            cost += (join_stats.get_size(joins[i]) + join_stats.get_size(min_size)) * min_selectivity
            explored_joins.append(joins[i])

    return cost

def evaluate(joins, join_stats): 
    left_parsed = False
    left_size = 0
    right_size = 0

    left_set = []
    right_set = []
    for index in range(len(joins)): 
        join = joins[index]
        if join != '?':
            if not left_parsed:
                if (index == len(joins)-1):
                    right_set.append(join)
                else: 
                    left_set.append(join)
            else: 
                right_set.append(join)
        else:
            left_size = calculate_sequence_cost(left_set, join_stats)
            left_parsed = True


        if (index == len(joins)-1): 
            print(left_set, right_set)
            right_size = calculate_sequence_cost(right_set, join_stats)
            print(left_size, right_size)


    selectivity = get_lowest_selectivity(left_set, right_set, join_stats)
    print(selectivity)
    cost = (left_size + right_size) * selectivity

    return cost



# stats = JoinStats('Join-Selectivities.xlsx')
# joins = ['company_name', 'role_type', 'company_type', 'movie_companies', 'title', 'cast_info', 'char_name']

# print("COST: ",evaluate(joins, stats))
