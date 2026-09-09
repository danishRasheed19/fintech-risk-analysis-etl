import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import pandas as pd
def get_connection():
    try:
        connection = psycopg2.connect(
            host = 'localhost',
            port = 5432,
            database = "Staging_risk",
            user = 'postgres',
            password = 'osaka@19'
        )
        
        print("POSTGRES CONNECTION SUCCESSFUL")
        
        return connection
    except psycopg2.Error as e:
        print(f"POSTGRESQL CONNECTION ERROR: {e}")
        raise
    
def load_dataframe(df,table_name):
    conncetion = get_connection()
    cursor = conncetion.cursor()
    try:
        columns = list(df.columns)
        query = f"""
         INSERT INTO staging.{table_name}
        ({','.join(columns)})
        VALUES %s
        """
        values = list(df.itertuples(index=False,name=None))
        execute_values(cursor,query,values)
        conncetion.commit()
        print(f"{table_name}: PostgreSQL loading successful")
    except psycopg2.Error as e:
        conncetion.rollback()
        print(f"{table_name}: POSTGRESQL LOADING ERROR: {e}")
        raise
    finally:
        cursor.close()
        conncetion.close()

def get_existing_ids(table_name,column_name):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = f"""
        SELECT {column_name} from staging.{table_name}
        """
        cursor.execute(query)
        ids = {row[0] for row in cursor.fetchall()}
        return ids
    except psycopg2.Error as e:
        print(f"Error while fetching ids for: {table_name} , {e}")
        raise
    finally:
        cursor.close()
        connection.close()
        
def get_existing_accounts():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        query = """
            SELECT account_id, created_at
            FROM staging.accounts
        """

        cursor.execute(query)

        accounts = cursor.fetchall()

        return pd.DataFrame(
            accounts,
            columns=["account_id", "created_at"]
        )

    except psycopg2.Error as e:

        print(f"ERROR WHILE FETCHING EXISTING ACCOUNTS: {e}")
        raise

    finally:

        cursor.close()
        connection.close()