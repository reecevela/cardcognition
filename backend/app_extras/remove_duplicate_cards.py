from dotenv import load_dotenv
import os
from pathlib import Path
import psycopg2

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

# Identify cards with the same name for the same commander
cur.execute("""
    SELECT commander_id, card_name, COUNT(*) FROM edhrec_cards
    GROUP BY commander_id, card_name
    HAVING COUNT(*) > 1
""")
duplicate_cards = cur.fetchall()
print(duplicate_cards)

# Remove the duplicate cards
for card in duplicate_cards:
    cur.execute("""
        DELETE FROM edhrec_cards
        WHERE id IN (
            SELECT id FROM edhrec_cards
            WHERE commander_id = %s AND card_name = %s
            ORDER BY id ASC
            LIMIT %s
        )
    """, (card[0], card[1], card[2] - 1))
    conn.commit()