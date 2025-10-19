# import psycopg2
# import csv
# from ..app.core.config import host,database,user,password,port

# # Database connection details
# DB_HOST = host
# DB_NAME = database
# DB_USER = user
# DB_PASSWORD = password
# DB_PORT = port

# CSV_FILE_PATH = "path/to/your/file.csv"
# TABLE_NAME = "sensor_readings"

# try:
#     # Establish connection
#     conn = psycopg2.connect(
#         host=DB_HOST,
#         database=DB_NAME,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         port=DB_PORT
#     )
#     cursor = conn.cursor()

#     # Open the CSV file and use the COPY command
#     with open(r"ai_assistant_project\data\sensors_dataset.csv", 'r') as f:
#         # Skip the header row if your CSV has one
#         next(f) 
#         cursor.copy_from(f, TABLE_NAME, sep=',', columns=('column1', 'column2', 'column3')) 
#         # Replace 'column1', 'column2', 'column3' with your actual column names in the correct order

#     # Commit the transaction
#     conn.commit()
#     print(f"Data from {CSV_FILE_PATH} successfully imported into {TABLE_NAME}.")

# except psycopg2.Error as e:
#     print(f"Error connecting to PostgreSQL or importing data: {e}")
#     if conn:
#         conn.rollback() # Rollback in case of error
# finally:
#     if cursor:
#         cursor.close()
#     if conn:
#         conn.close()


import psycopg2
import csv
import pandas as pd
from ..app.core.config import host, database, user, password, port

# Database connection details
DB_HOST = host
DB_NAME = database
DB_USER = user
DB_PASSWORD = password
DB_PORT = port

CSV_FILE_PATH = r"ai_assistant_project\data\sensors_dataset.csv"
TABLE_NAME = "sensor_readings"

# Function to map pandas dtypes to PostgreSQL types
def get_postgres_type(dtype):
    if dtype == "int64":
        return "INTEGER"
    elif dtype == "float64":
        return "FLOAT"
    elif dtype == "bool":
        return "BOOLEAN"
    elif dtype == "datetime64[ns]":
        return "TIMESTAMP"
    else:
        return "TEXT"  # Fallback for unknown types (e.g., object)

try:
    # Establish connection
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Read CSV to get column names and infer types using pandas
    df = pd.read_csv(CSV_FILE_PATH, nrows=1)  # Read only the header to get columns
    columns = df.columns.tolist()
    dtypes = df.dtypes

    # Create table with columns matching CSV
    create_table_query = f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} ("
    for col, dtype in zip(columns, dtypes):
        pg_type = get_postgres_type(str(dtype))
        create_table_query += f'"{col}" {pg_type}, '
    create_table_query = create_table_query.rstrip(", ") + ");"
    
    # Execute table creation
    cursor.execute(create_table_query)
    print(f"Table {TABLE_NAME} created or already exists.")

    # Open the CSV file and use COPY command
    with open(CSV_FILE_PATH, 'r') as f:
        next(f)  # Skip the header row
        cursor.copy_from(f, TABLE_NAME, sep=',', columns=columns)

    # Commit the transaction
    conn.commit()
    print(f"Data from {CSV_FILE_PATH} successfully imported into {TABLE_NAME}.")

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL or importing data: {e}")
    if conn:
        conn.rollback()
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()