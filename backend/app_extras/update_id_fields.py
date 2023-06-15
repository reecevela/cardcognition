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

# Create an array of each card name in the edhrec_cards table
# Only get the card names that don't have a Scryfall ID
cur.execute("""
    SELECT card_name FROM edhrec_cards
    WHERE scryfall_id IS NULL
""")
card_names = cur.fetchall()

# Format them by removing special characters and spaces and keep both original and formatted names
formatted_card_names = [(card_name[0], card_name[0].replace("'", "").replace(",", "").replace(" ", "-").replace("&", "").lower()) for card_name in card_names]

# Remove duplicates
formatted_card_names = list(set(formatted_card_names))

# Get the Scryfall ID for each card
for original_card, formatted_card in formatted_card_names:
    print(f"Getting Scryfall ID for {formatted_card}")
    # Get the card data from Scryfall
    response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={formatted_card}")
    if response.status_code != 200:
        print(f"Error: {response.status_code} for card {formatted_card}")
        continue
    card_data = response.json()
    card_scryfall_id = card_data['id']
    # assign the Scryfall ID to the card in the database
    cur.execute("""
        UPDATE edhrec_cards
        SET scryfall_id = %s
        WHERE card_name = %s
    """, (card_scryfall_id, original_card))
    conn.commit()

    # Pull the card data from the database
    cur.execute("""
        SELECT card_name, scryfall_id FROM edhrec_cards
        WHERE card_name = %s
    """, (original_card,))
    card_data = cur.fetchone()
    print(card_data)
