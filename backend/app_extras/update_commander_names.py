from sql_executer import sql_executer
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

# Create the scryfall_id column in the edhrec_commanders table
sql_executer("""
    ALTER TABLE edhrec_commanders
    ADD COLUMN scryfall_id VARCHAR(255)
""")

# Get the list of commanders from the database
commanders = sql_executer("""
    SELECT name FROM edhrec_commanders
    WHERE scryfall_id IS NULL
""")

# Get the scryfall ID for each commander
for commander in commanders:
    print(f"Getting Scryfall ID for {commander[0]}") # kruphix-god-of-horizons for Kruphix, God of Horizons

    # If the commander name has an & symbol, replace it with %26
    if "&" in commander[0]:
        commander = [commander[0].replace("&", "%26")]

    # Get the card data from Scryfall
    response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={commander[0]}")
    if response.status_code != 200:
        print(f"Error: {response.status_code} for commander {commander[0]}")
        continue
    card_data = response.json()
    card_scryfall_id = card_data['id']
    # assign the Scryfall ID to the commander in the database
    cur.execute("""
        UPDATE edhrec_commanders
        SET scryfall_id = %s
        WHERE name = %s
    """, (card_scryfall_id, commander[0]))
    conn.commit()
    

