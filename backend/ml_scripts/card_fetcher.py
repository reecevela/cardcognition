from pathlib import Path
import psycopg2
import os
from dotenv import load_dotenv
from converter import MLConverter

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
    # 22901	"55552a2b-1861-4235-a60d-ccabb4839d54"	"Aura Graft"	"{1}{U}"	2	    "Instant"	"Gain control of target Aura that's attached to a permanent. Attach it to ansub permanent it can enchant."	"U"	"U"	true	"10e"	"uncommon"	"{""usd"": ""0.18"", ""usd_foil"": ""0.62"", ""usd_etched"": null, ""eur"": ""0.09"", ""eur_foil"": ""0.39"", ""tix"": ""0.02""}"	17200
    # (Cont.)
    # "colors" "color_identity" "commander_legal"	"set_code"	"rarity"	"edhrec_rank"   "prices"
    # "U"	    "U"	            true	            "10e"	    "uncommon"	17200           "{""usd"": ""0.18"", ""usd_foil"": ""0.62"", ""usd_etched"": null, ""eur"": ""0.09"", ""eur_foil"": ""0.39"", ""tix"": ""0.02""}"

    def fetch_list_of_dicts(self, cursor)-> list:
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_all_cards(self) -> list:
        self.cur.execute("""
            SELECT * FROM scryfall_cards
            WHERE commander_legal = true
        """)
        return self.fetch_list_of_dicts(self.cur)
    
    def get_all_card_types_and_sub_types(self):
        self.cur.execute("""
            SELECT type_line
            FROM scryfall_cards
        """)
        card_types = set()
        sub_types = set()
        for row in self.cur.fetchall():
            card_type, sub_types_list = self.process_type_line(row[0])
            card_types.add(card_type)
            sub_types.update(sub_types_list)
        return list(card_types), list(sub_types)

    def process_type_line(self, type_line: str):
        return MLConverter().process_type_line(type_line)

        
    def get_card_by_id(self, card_id:int) -> dict:
        self.cur.execute("""
            SELECT * FROM scryfall_cards
            WHERE id = %s
            AND commander_legal = true
        """, (card_id,))
        return self.fetch_list_of_dicts(self.cur)[0]

    def get_commanders(self) -> list:
        self.cur.execute("""
            SELECT * FROM scryfall_cards
            WHERE id IN (
                SELECT card_id FROM edhrec_commanders
            ) AND commander_legal = true
        """)
        return self.fetch_list_of_dicts(self.cur)
    
    def get_commander_by_id(self, commander_id:int) -> dict:
        self.cur.execute("""
            SELECT * FROM edhrec_commanders
            WHERE id = %s
            AND commander_legal = true
        """, (commander_id,))
        return self.fetch_list_of_dicts(self.cur)[0]
    
    def get_commander_synergies_by_id(self, commander_id:int) -> list:
        self.cur.execute("""
            SELECT card_id, synergy_score FROM edhrec_cards
            WHERE commander_id = %s
            AND commander_legal = true
        """, (commander_id,))
        return self.fetch_list_of_dicts(self.cur)
    
    def get_card_synergies_by_id(self, card_id:int) -> list:
        self.cur.execute("""
            SELECT commander_id, synergy_score FROM edhrec_cards
            WHERE card_id = %s
            AND commander_legal = true
        """, (card_id,))
        return self.fetch_list_of_dicts(self.cur)
    
    def get_card_batch_by_id(self, card_ids:list) -> list:
        self.cur.execute("""
            SELECT * FROM scryfall_cards
            WHERE id = ANY(%s)
        """, (card_ids,))
        return self.fetch_list_of_dicts(self.cur)
    
    def get_commander_batch_by_id(self, commander_ids:list) -> list:
        self.cur.execute("""
            SELECT [sc].* FROM scryfall_cards sc
            INNER JOIN edhrec_commanders ec
            ON sc.id = ec.card_id
            WHERE sc.id = ANY(%s)
        """, (commander_ids,))
        return self.fetch_list_of_dicts(self.cur)