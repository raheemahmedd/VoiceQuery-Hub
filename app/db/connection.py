import psycopg2

from ..core.config import host,database,user,password,port

def db_connection():
    connection=None
 
    try:
        connection = psycopg2.connect(
            host=host,         
            database=database,
            user=user,
            password=password,
            port=port               
        )
        print("Connection to PostgreSQL successful!")

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")

    return connection
if __name__ == '__main__':
    db_connection()