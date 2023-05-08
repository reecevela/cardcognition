from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
import os
from pathlib import Path
import psycopg2
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

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

# Create the table to store the commander data
cur.execute("""
CREATE TABLE IF NOT EXISTS edhrec_commanders (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
)
""")
conn.commit()

# Create the table to store the card data
cur.execute("""
CREATE TABLE IF NOT EXISTS edhrec_cards (
    id SERIAL PRIMARY KEY,
    commander_id INTEGER,
    card_name TEXT,
    percentage NUMERIC,
    num_decks INTEGER,
    synergy_score NUMERIC
)
""")
conn.commit()

def scrape_commander_data(commander_name: str):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    url = f'https://edhrec.com/commanders/{commander_name.replace(" ", "-").lower()}'
    driver.get(url)

    time.sleep(5)

    # Scrape the card data
    card_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "Card_container")]')

    # Save the commander in the database
    cur.execute("""
    INSERT INTO edhrec_commanders (name) VALUES (%s)
    ON CONFLICT (name) DO UPDATE
    SET name = EXCLUDED.name
    RETURNING id
    """, (commander_name,))
    commander_id = cur.fetchone()[0]
    conn.commit()

    for card_element in card_elements[1:]:
        card_name_element = card_element.find_element(By.XPATH, './/span[contains(@class, "Card_name")]')
        card_name = card_name_element.text
        percentage_info_element = card_element.find_element(By.XPATH, './/div[contains(@class, "CardLabel_label")]')
        percentage_info = percentage_info_element.text

        print(card_name)
        print(percentage_info)
        # Extract the numbers from the percentage info string
        inclusion_rate, total_decks, synergy = map(int, re.findall(r'(\d+)%\s+of\s+(\d+)\s+decks\s*\n?\s*([\+\-]\d+)%', percentage_info)[0])

        # Calculate the base inclusion rate
        base_inclusion_rate = inclusion_rate - synergy

        # Calculate the synergy score
        synergy_score = inclusion_rate / base_inclusion_rate if base_inclusion_rate != 0 else 100

        print(card_name)
        print(f"Inclusion rate: {inclusion_rate}")
        print(f"Total decks: {total_decks}")
        print(f"Synergy score: {synergy_score}")

        # Save the card data in the database
        cur.execute("""
        INSERT INTO edhrec_cards (commander_id, card_name, percentage, num_decks, synergy_score)
        VALUES (%s, %s, %s, %s, %s)
        """, (commander_id, card_name, inclusion_rate, total_decks, synergy_score))
        conn.commit()

    # Close the WebDriver
    driver.quit()

def get_highest_synergy_score(commander_name: str):
    cur.execute("""
    SELECT c.card_name, c.synergy_score
    FROM edhrec_cards c
    JOIN edhrec_commanders cmd ON c.commander_id = cmd.id
    WHERE cmd.name = %s
    ORDER BY c.synergy_score DESC
    LIMIT 1
    """, (commander_name,))
    result = cur.fetchone()
    return result

# Example usage
commander = "korvold-fae-cursed-king"
scrape_commander_data(commander)
highest_synergy = get_highest_synergy_score(commander)
print(f"Highest synergy card for {commander}: {highest_synergy}")
# Close the database connection
cur.close()
conn.close()