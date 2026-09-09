from datetime import datetime
import psycopg2
from load.postgres_loader import get_connection


def get_watermark(dataset):
    # watermarks = load_watermarks()
    print(f"GETTING WATERMARK FOR {dataset}")
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = """
        SELECT watermark from metadata.watermarks 
        where dataset_name = %s
        """
        cursor.execute(query,(dataset,))
        watermark = cursor.fetchone()[0]
        return watermark
    except psycopg2.Error as e:
        print(f"POSTGRESQL CONNECTION ERROR: {e}")
        raise
    finally:
        cursor.close()
        connection.close()

def set_watermarks(dataset,timestamp):
    print(f"UPDATING WATERMARK FOR: {dataset}")
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = f"""
        UPDATE metadata.watermarks 
        SET
        watermark = %s,
        updated_at = CURRENT_TIMESTAMP
        where dataset_name = %s
        """      
        if isinstance(timestamp,datetime):
            timestamp = timestamp.isoformat()
            
        cursor.execute(query,(timestamp,dataset))
        if cursor.rowcount == 0:
            raise ValueError(
                f"Unsupported dataset for watermarking: {dataset}"
            )
        connection.commit()
    except psycopg2.Error as e:
        connection.rollback()
        print(f"ERROR while updating watermark for {dataset}: {e}")
        raise
    finally:
        cursor.close()
        connection.close()