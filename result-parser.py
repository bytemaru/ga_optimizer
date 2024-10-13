import re
from collections import defaultdict

# Initialize variables
query_data = defaultdict(lambda: {'costs': [], 'num_joins': 0})

# Regular expressions to match relevant lines
query_re = re.compile(r'Query: \./ENGR489-Project/TestQueries/(\w+).sql')
cost_re = re.compile(r'Cost: ([\d.]+)')
join_order_re = re.compile(r"Optimal Join Order: \[(.*?)\]")

# Read the file
with open('results/improved-cost-calc-nosplit.txt', 'r') as file:
    current_query = None
    for line in file:
        query_match = query_re.search(line)
        cost_match = cost_re.search(line)
        join_order_match = join_order_re.search(line)
        
        if query_match:
            current_query = query_match.group(1)
        elif cost_match and current_query:
            cost = float(cost_match.group(1))
            query_data[current_query]['costs'].append(cost)
        elif join_order_match and current_query:
            # Count the number of joins (strings in the optimal join order array)
            num_joins = len(join_order_match.group(1).split(', '))
            query_data[current_query]['num_joins'] = num_joins

# Calculate and print the average cost and the number of joins for each query
for query, data in query_data.items():
    avg_cost = sum(data['costs']) / len(data['costs'])
    num_joins = data['num_joins']
    print(f"Query: {query}, Number of Joins: {num_joins}, Average Cost: {avg_cost:.2f}")
