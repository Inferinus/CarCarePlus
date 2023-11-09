import sqlite3

# Replace 'your_database.db' with the path to your actual database file
database_path = 'carcareplus.db'

# Connect to the SQLite database
conn = sqlite3.connect(database_path)

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Retrieve the list of all the tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print the schema of each table
for table_name in tables:
    table_name = table_name[0]
    print(f"Schema of table '{table_name}':")
    cursor.execute(f"PRAGMA table_info('{table_name}');")
    # Get columns information
    columns_info = cursor.fetchall()
    for col_info in columns_info:
        print(col_info)
    print()

# Close the connection
conn.close()
