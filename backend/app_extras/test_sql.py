from dotenv import load_dotenv
import os
from pathlib import Path
import psycopg2
import requests

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

# print number of unique card_names
cur.execute("""
    SELECT COUNT(DISTINCT card_name) FROM edhrec_cards
""")
print(f"Unique cards: {cur.fetchone()[0]}")

# print number of cards total:
cur.execute("""
    SELECT COUNT(*) FROM edhrec_cards
""")
print(f"Total cards: {cur.fetchone()[0]}")

# print number of unique card_name values with null scryfall_id
cur.execute("""
    SELECT COUNT(DISTINCT card_name) FROM edhrec_cards
    WHERE scryfall_id IS NULL
""")
print(f"Unique cards without a scryfall_id: {cur.fetchone()[0]}")

# print number of cards without a scryfall_id
cur.execute("""
    SELECT COUNT(*) FROM edhrec_cards
    WHERE scryfall_id IS NULL
""")
print(f"Cards without a scryfall_id: {cur.fetchone()[0]}")
