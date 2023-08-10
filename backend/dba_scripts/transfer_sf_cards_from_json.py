from dotenv import load_dotenv
import os
from pathlib import Path
import psycopg2
import json

def configure_db():
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

    return conn, cur

def insert_cards_json(cards):
    conn, cur = configure_db()

    insert_sql = '''
        INSERT INTO scryfall_cards (
            scryfall_id,
            card_name,
            mana_cost,
            cmc,
            type_line,
            oracle_text,
            colors,
            color_identity,
            commander_legal,
            set_code,
            rarity,
            prices,
            edhrec_rank
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    '''

    existing_cards = set()
    cur.execute('SELECT scryfall_id FROM scryfall_cards')
    for card in cur.fetchall():
        existing_cards.add(card[0])

    card_tuples = []
    for card in cards:
        commander_legal_status = True if card['legalities']['commander'] == "legal" else False
        
        card_details = (
            card['id'],
            card['name'],
            card.get('mana_cost', None),
            card.get('cmc', None),
            card['type_line'],
            card.get('oracle_text', None),
            ''.join(card.get('colors', [])),
            ''.join(card.get('color_identity', [])),
            commander_legal_status,
            card['set'],
            card['rarity'],
            json.dumps(card.get('prices', {})),
            card.get('edhrec_rank', None),
        )

        if card['cmc'] == 1000000: # Gleemax smh
            continue

        if card['id'] not in existing_cards:
            card_tuples.append(card_details)

    try:
        cur.executemany(insert_sql, card_tuples)

        # Commit the changes and close the connection
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(e)

def update_cards_json(cards):
    conn, cur = configure_db()

    update_sql = '''
        UPDATE scryfall_cards
        SET mana_cost = %s,
            cmc = %s,
            type_line = %s,
            oracle_text = %s,
            colors = %s,
            color_identity = %s,
            commander_legal = %s,
            set_code = %s,
            rarity = %s,
            prices = %s,
            edhrec_rank = %s
        WHERE card_name = %s
    '''

    existing_cards = set()
    cur.execute('SELECT card_name FROM scryfall_cards WHERE mana_cost IS NULL')
    for card in cur.fetchall():
        existing_cards.add(card[0])

    card_tuples = []
    for card in cards:
        commander_legal_status = True if card['legalities']['commander'] == "legal" else False
        
        card_details = (
            card.get('mana_cost', None),
            card.get('cmc', None),
            card['type_line'],
            card.get('oracle_text', None),
            ''.join(card.get('colors', [])),
            ''.join(card.get('color_identity', [])),
            commander_legal_status,
            card['set'],
            card['rarity'],
            json.dumps(card.get('prices', {})),
            card.get('edhrec_rank', None),
            card['name'],
        )

        if card['name'] in existing_cards:
            card_tuples.append(card_details)
     
    try:
        cur.executemany(update_sql, card_tuples)

        # Commit the changes and close the connection
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(e)

def remove_tokens(data):
    conn, cur = configure_db()

    token_ids = set()
    for card in data:
        if card.get('type_line', '').startswith('Token'):
            if card.get('id', None) is None:
                continue
            token_ids.add(card['id'])

    try:
        cur.executemany('DELETE FROM scryfall_cards WHERE scryfall_id = %s', [(token_id,) for token_id in token_ids])

        # Commit the changes and close the connection
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(e)

with open(r"C:\Scryfall Cards\cards08082023.json", 'r', encoding="utf-8") as file:
    data = json.load(file)

update_cards_json(data)