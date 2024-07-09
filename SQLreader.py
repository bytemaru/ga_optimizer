import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
import itertools
import pandas as pd

def is_subselect(parsed):
    if not parsed.is_group:
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            return True
    return False

def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        if from_seen:
            if is_subselect(item):
                for x in extract_from_part(item):
                    yield x
            elif item.ttype is Keyword:
                return
            else:
                yield item
        elif item.ttype is Keyword and item.value.upper() == 'FROM':
            from_seen = True

def extract_table_identifiers(token_stream):
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                yield identifier.get_real_name()
        elif isinstance(item, Identifier):
            yield item.get_real_name()
        elif item.ttype is Keyword:
            yield item.value

def parse_sql(sql):
    parsed = sqlparse.parse(sql)[0]
    from_clause = list(extract_from_part(parsed))
    tables = list(extract_table_identifiers(from_clause))

    query_dict = {
        "SELECT": [],
        "FROM": tables,
        "WHERE": [],
        "JOIN": []
    }

    # Extract SELECT part
    select_seen = False
    for token in parsed.tokens:
        if token.ttype is DML and token.value.upper() == 'SELECT':
            select_seen = True
        elif select_seen:
            if token.ttype is Keyword and token.value.upper() == 'FROM':
                break
            if token.ttype is not None and token.ttype is not Keyword:
                query_dict["SELECT"].append(token.value.strip())

    # Extract WHERE part
    where_seen = False
    for token in parsed.tokens:
        if token.ttype is Keyword and token.value.upper() == 'WHERE':
            where_seen = True
        elif where_seen:
            if token.ttype is Keyword and token.value.upper() in ('GROUP', 'ORDER', 'LIMIT'):
                break
            if token.ttype is not None:
                query_dict["WHERE"].append(token.value.strip())

    # Extract JOIN part
    join_seen = False
    for token in parsed.tokens:
        if token.ttype is Keyword and 'JOIN' in token.value.upper():
            join_seen = True
            query_dict["JOIN"].append(token.value.strip())
        elif join_seen:
            if token.ttype is Keyword and token.value.upper() in ('ON', 'USING'):
                join_seen = False
                query_dict["JOIN"][-1] += ' ' + token.value.strip()
            elif token.ttype is not None:
                query_dict["JOIN"][-1] += ' ' + token.value.strip()

    return query_dict

# Function to read SQL from a file
def read_sql_from_file(file_path):
    with open(file_path, 'r') as file:
        sql_query = file.read()
    return sql_query

# Function to read join statistics from an Excel file without labeled columns
def read_join_stats_from_excel(file_path):
    df = pd.read_excel(file_path, header=None, usecols=[0, 1, 2, 3, 4])
    df.columns = ['table1_name', 'table2_name', 'table1_size', 'table2_size', 'selectivity']
    join_stats = {}
    for _, row in df.iterrows():
        table1 = row['table1_name']
        table2 = row['table2_name']
        size1 = row['table1_size']
        size2 = row['table2_size']
        selectivity = row['selectivity']
        cost = (size1 + size2) * selectivity
        join_stats[(table1, table2)] = cost
        join_stats[(table2, table1)] = cost  # Assuming join cost is symmetric
    return join_stats

# Function to find the optimal join order
def find_optimal_join_order(tables, join_stats):
    min_cost = float('inf')
    best_order = None
    for perm in itertools.permutations(tables):
        cost = 0
        for i in range(1, len(perm)):
            cost += join_stats.get((perm[i-1], perm[i]), float('inf'))
        if cost < min_cost:
            min_cost = cost
            best_order = perm
    return best_order, min_cost

# Paths to the SQL file and Excel file
sql_file_path = 'join-order-benchmark/1a.sql'
excel_file_path = 'Join-Selectivities.xlsx'

# Read the SQL query from the file
sql_query = read_sql_from_file(sql_file_path)

# Parse the query
parsed_query = parse_sql(sql_query)
for key, value in parsed_query.items():
    print(f"{key}: {value}")

# Read the join statistics from the Excel file
join_stats = read_join_stats_from_excel(excel_file_path)

# Find and print the optimal join order and its cost
optimal_order, cost = find_optimal_join_order(parsed_query["FROM"], join_stats)
print(f"Optimal Join Order: {optimal_order}")
print(f"Cost: {cost}")