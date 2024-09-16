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

def calculate_sequence_size(joins, join_stats): 
    total_size= 0
    explored_joins = []
    for join in joins:
        total_size += join_stats.get_size(join)
    return total_size

def get_lowest_selectivity(left_set, right_set, join_stats): 
    best_selectivity = 10000
    for left in left_set: 
        for right in right_set: 
            selectivity = join_stats.get_selectivity(left, right)
            if selectivity < best_selectivity: 
                best_selectivity = selectivity
                print(left, right)
    return best_selectivity


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
                if (index == len(joins)-2):
                    right_set.append(join)
                else: 
                    left_set.append(join)
            else: 
                right_set.append(join)
        else:
            left_size = calculate_sequence_size(left_set, join_stats)
            left_parsed = True

        if (index == len(joins)-1): 
            right_size = calculate_sequence_size(right_set, join_stats)

    selectivity = get_lowest_selectivity(left_set, right_set, join_stats)
    cost = (left_size + right_size) * selectivity
    print(left_set)
    print(right_set)
    print(left_size, right_size, selectivity)

    return cost



stats = JoinStats('Join-Selectivities.xlsx')
joins = ['company_name', 'role_type', 'company_type', 'movie_companies', '?', 'title', 'cast_info', 'char_name']

print("COST: ",evaluate(joins, stats))
