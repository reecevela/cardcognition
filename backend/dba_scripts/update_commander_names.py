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

# Get the list of commanders from the database
commanders = cur.execute("""
    SELECT scryfall_id FROM edhrec_commanders
    WHERE card_name IS NULL
""").fetchall()

# Get the actual card name for each commander
for commander in commanders[1:]:
    # Get the scryfall_id for the commander
    scryfall_id = commander[0]

    # Get the card name from the scryfall API
    card = requests.get(f'https://api.scryfall.com/cards/{scryfall_id}').json()
    card_name = card['name']
    print(card_name)

    # Update the card_name column in the database
    cur.execute("""
        UPDATE edhrec_commanders
        SET card_name = %s
        WHERE scryfall_id = %s
    """, (card_name, scryfall_id))

    # Commit the changes
    conn.commit()

