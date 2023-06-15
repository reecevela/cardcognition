from dotenv import load_dotenv
import os
from pathlib import Path
import psycopg2
import requests

def sql_executer(sql):

    try:
        BASE_DIR = Path(__file__).resolve().parent.parent
        load_dotenv(os.path.join(BASE_DIR, '.env'))

        # Database Configuration
        DB_NAME = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')

        # Connect to the database
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()

        # Execute the SQL
        cur.execute(sql)
        conn.commit()

        return (cur.fetchall())

    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    print(sql_executer("""
        SELECT COUNT(*) FROM edhrec_cards
    """))
