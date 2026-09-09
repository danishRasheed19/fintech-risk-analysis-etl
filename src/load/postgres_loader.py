import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
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


def main():
    load_dataframe("mdfs","Temp table")
    
if __name__ == "__main__":
    main()