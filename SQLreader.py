import pandas as pd
import re

# Step 1: Read table sizes and selectivity from Excel
excel_file = "your_excel_file.xlsx"  # Update with your file path
df = pd.read_excel(excel_file)

# Extract table sizes and selectivity
table_sizes = df.set_index('Table').to_dict()['Size']
selectivity = df.set_index('Condition').to_dict()['Selectivity']

# Step 2: Parse SQL query from SQL file
sql_file = "your_sql_file.sql"  # Update with your file path
with open(sql_file, 'r') as file:
    sql_query = file.read()

# Extract table names from the query
table_names = re.findall(r'FROM\s+(\w+)\s+AS\s+\w+', sql_query, re.IGNORECASE)

# Step 3: Calculate estimated cost
estimated_cost = sum(table_sizes[table] * selectivity[table] for table in table_names)

# Print estimated cost
print("Estimated cost of the SQL query:", estimated_cost)