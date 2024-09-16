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

def calculate_join_seq(joins, join_stats): 
    cost = 0
    explored_joins = []
    for i in range(1, len(joins)):
        join1 = joins[i-1]
        join2 = joins[i]
        print(join1, join2)
        if len(explored_joins) == 0: 
            size1 = join_stats.get_size(join1)
            size2 = join_stats.get_size(join2)
            selectivity = join_stats.get_selectivity(join1, join2)
            cost += (size1 + size2) * selectivity
            explored_joins.append(join1)
            explored_joins.append(join2)
            print("TEST", size1, size2, selectivity, cost)
        else: 
            curr_join = joins[i]
            best_join = ''
            min_selectivity = 10000
            for join in explored_joins: 
                selectivity = join_stats.get_selectivity(join, curr_join)
                if selectivity < min_selectivity:
                    best_join = join
                    min_selectivity = selectivity
            size1 = join_stats.get_size(curr_join)
            size2 = join_stats.get_size(best_join)
            cost += (size1 + size2) * min_selectivity
            explored_joins.append(curr_join)
            explored_joins.append(best_join)
            print("TESTING: ", size1,size2,min_selectivity,cost)
    return cost


def evaluate(joins, join_stats): 
    prev_cost = 0
    curr_cost = 0
    parsed_set = []
    for index in range(len(joins)): 
        join = joins[index]
        if join != '?':
            parsed_set.append(join)
            print("parsed", parsed_set)
        elif (join == '?'):
            print("parsed", parsed_set)
            prev_cost = calculate_join_seq(parsed_set, join_stats)
            parsed_set = []
        if (index == len(joins)-1): 
            print("parsed brah", parsed_set)
            curr_cost = calculate_join_seq(parsed_set, join_stats)
            print("ESHAY: ", curr_cost)
        print("bomboclat: ", index)
        print("current join: ", join, prev_cost, curr_cost)

    return (prev_cost + curr_cost)/2



stats = JoinStats('Join-Selectivities.xlsx')
joins = ['company_name', 'role_type', 'company_type', '?', 'movie_companies', 'title', 'cast_info', 'char_name']
print(stats.get_selectivity('title', 'name'))
print("COST: ",evaluate(joins, stats))
