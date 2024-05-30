import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
import itertools

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

# Mock cost function for joins
def join_cost(tables, stats):
    cost = 0
    for i in range(1, len(tables)):
        cost += stats[tables[i-1]] * stats[tables[i]]
    return cost

# Function to find the optimal join order
def find_optimal_join_order(tables, stats):
    min_cost = float('inf')
    best_order = None
    for perm in itertools.permutations(tables):
        cost = join_cost(perm, stats)
        if cost < min_cost:
            min_cost = cost
            best_order = perm
    return best_order, min_cost

# Define your SQL query
sql_query = """
SELECT MIN(mc.note) AS production_note,
       MIN(t.title) AS movie_title,
       MIN(t.production_year) AS movie_year
FROM company_type AS ct,
     info_type AS it,
     movie_companies AS mc,
     movie_info_idx AS mi_idx,
     title AS t
WHERE ct.kind = 'production companies'
  AND it.info = 'top 250 rank'
  AND mc.note NOT LIKE '%(as Metro-Goldwyn-Mayer Pictures)%'
  AND (mc.note LIKE '%(co-production)%'
       OR mc.note LIKE '%(presents)%')
  AND ct.id = mc.company_type_id
  AND t.id = mc.movie_id
  AND t.id = mi_idx.movie_id
  AND mc.movie_id = mi_idx.movie_id
  AND it.id = mi_idx.info_type_id;
"""

# Parse the query
parsed_query = parse_sql(sql_query)
for key, value in parsed_query.items():
    print(f"{key}: {value}")

# Define mock table statistics
table_stats = {
    "company_type": 1000,
    "info_type": 500,
    "movie_companies": 2000,
    "movie_info_idx": 1500,
    "title": 1000
}

# Find and print the optimal join order and its cost
optimal_order, cost = find_optimal_join_order(parsed_query["FROM"], table_stats)
print(f"Optimal Join Order: {optimal_order}")
print(f"Cost: {cost}")
