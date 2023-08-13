from pathlib import Path
import psycopg2
import os
from dotenv import load_dotenv

class CardsContext:
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        load_dotenv(os.path.join(self.BASE_DIR, '..\.env'))

        # Database Configuration
        self.db_config = {
            'name': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }

        # Connect to the database
        self.conn = psycopg2.connect(
            dbname=self.db_config['name'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            host=self.db_config['host'],
            port=self.db_config['port']
        )
        self.cur = self.conn.cursor()

    # DB Columns and example data but in JSON format for readability:
    # edhrec_commanders table
    #   "id"	"name"	                    "scryfall_id"	                        "card_name"	            "card_id"
    #   7	    "abaddon-the-despoiler"	    "c9f1fc97-00c0-492b-a4a3-b179afc2f95d"	"Abaddon the Despoiler"	20423
    #
    # edhrec_cards table
    #   "id"	"commander_id"	"percentage"	"num_decks"	"synergy_score"	"card_id"
    #   173993	748	            24	            2392	    12.0	        27164
    #
    # scryfall_cards table
    # "id"	"scryfall_id"	                        "card_name"	    "mana_cost"	"cmc"	"type_line"	"oracle_text"
    # 22901	"55552a2b-1861-4235-a60d-ccabb4839d54"	"Aura Graft"	"{1}{U}"	2	    "Instant"	"Gain control of target Aura that's attached to a permanent. Attach it to another permanent it can enchant."	"U"	"U"	true	"10e"	"uncommon"	"{""usd"": ""0.18"", ""usd_foil"": ""0.62"", ""usd_etched"": null, ""eur"": ""0.09"", ""eur_foil"": ""0.39"", ""tix"": ""0.02""}"	17200
    # (Cont.)
    # "colors" "color_identity" "commander_legal"	"set_code"	"rarity"	"edhrec_rank"   "prices"
    # "U"	    "U"	            true	            "10e"	    "uncommon"	17200           "{""usd"": ""0.18"", ""usd_foil"": ""0.62"", ""usd_etched"": null, ""eur"": ""0.09"", ""eur_foil"": ""0.39"", ""tix"": ""0.02""}"

    def get_all_cards(self) -> list:
        self.cur.execute("""
            SELECT * FROM scryfall_cards
        """)
        return self.cur.fetchall()
    
    def get_card_by_id(self, card_id:int) -> dict:
        self.cur.execute("""
            SELECT * FROM scryfall_cards
            WHERE id = %s
        """, (card_id,))
        return self.cur.fetchone()

    def get_commanders(self) -> list:
        self.cur.execute("""
            SELECT * FROM edhrec_commanders
        """)
        return self.cur.fetchall()
    
    def get_commander_by_id(self, commander_id:int) -> dict:
        self.cur.execute("""
            SELECT * FROM edhrec_commanders
            WHERE id = %s
        """, (commander_id,))
        return self.cur.fetchone()
    
    def get_commander_synergies_by_id(self, commander_id:int) -> list:
        self.cur.execute("""
            SELECT card_id, synergy_score FROM edhrec_cards
            WHERE commander_id = %s
        """, (commander_id,))
        return self.cur.fetchall()
    
    def get_card_synergies_by_id(self, card_id:int) -> list:
        self.cur.execute("""
            SELECT commander_id, synergy_score FROM edhrec_cards
            WHERE card_id = %s
        """, (card_id,))
        return self.cur.fetchall()
    
    def get_card_batch_by_id(self, card_ids:list) -> list:
        self.cur.execute("""
            SELECT * FROM scryfall_cards
            WHERE id = ANY(%s)
        """, (card_ids,))
        return self.cur.fetchall()
    
    def get_commander_batch_by_id(self, commander_ids:list) -> list:
        self.cur.execute("""
            SELECT * FROM edhrec_commanders
            WHERE id = ANY(%s)
        """, (commander_ids,))
        return self.cur.fetchall()