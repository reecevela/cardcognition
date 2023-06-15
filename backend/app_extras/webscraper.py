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
    synergy_score NUMERIC,
    CONSTRAINT unique_commander_card UNIQUE (commander_id, card_name)
)
""")
conn.commit()

def scrape_commander_data(commander_name: str):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    url = f'https://edhrec.com/commanders/{commander_name.replace(" ", "-").lower()}'
    driver.get(url)

    print(f"Scraping {commander_name}...")

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

    # Start the card timer
    start_time = time.time()

    card_list = []
    for card_element in card_elements[1:]:
        card_name_element = card_element.find_element(By.XPATH, './/span[contains(@class, "Card_name")]')
        card_name = card_name_element.text
        percentage_info_element = card_element.find_element(By.XPATH, './/div[contains(@class, "CardLabel_label")]')
        percentage_info = percentage_info_element.text

        # Extract the numbers from the percentage info string
        inclusion_rate, total_decks, synergy = map(int, re.findall(r'(\d+)%\s+of\s+(\d+)\s+decks\s*\n?\s*([\+\-]\d+)%', percentage_info)[0])

        # Calculate the base inclusion rate
        base_inclusion_rate = inclusion_rate - synergy

        # Calculate the synergy score
        synergy_score = round(inclusion_rate / base_inclusion_rate if base_inclusion_rate != 0 else inclusion_rate, 2)

        card_object = {
            "commander_id": commander_id,
            "card_name": card_name,
            "percentage": inclusion_rate,
            "num_decks": total_decks,
            "synergy_score": synergy_score
        }

        card_list.append(card_object)

    # Print the time it took to scrape the cards
    print(f"Scraped {len(card_list)} cards in {time.time() - start_time} seconds")

    # Reset the card timer
    start_time = time.time()

    # Save the card data in the database
    cur.executemany("""
    INSERT INTO edhrec_cards (commander_id, card_name, percentage, num_decks, synergy_score)
    VALUES (%(commander_id)s, %(card_name)s, %(percentage)s, %(num_decks)s, %(synergy_score)s)
    ON CONFLICT ON CONSTRAINT unique_commander_card DO UPDATE
    SET percentage = EXCLUDED.percentage, num_decks = EXCLUDED.num_decks, synergy_score = EXCLUDED.synergy_score
    """, card_list)

    conn.commit()

    # Print the time it took to save the cards
    print(f"Saved {len(card_list)} cards in {time.time() - start_time} seconds")

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

if __name__ == "__main__":
    # Scrape the commander data
    with open('commanders.txt', 'r') as f:
        commanders = f.readlines()
    
    midpoint = len(commanders) // 2

    for commander in commanders[1684:1899]:
        try:
            scrape_commander_data(commander.strip())
        except Exception as e:
            print(e)
            continue
    # Close the database connection
    cur.close()
    conn.close()