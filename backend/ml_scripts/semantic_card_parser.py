import re
import json
try:
    from ml_scripts.converter import MLConverter
except Exception as e:
    from converter import MLConverter

import spacy


class SemanticCardParser:
    def __init__(self):
        self.converter = MLConverter()

    def parse_card(self, card):
        out = []
        
        abilities = card['oracle_text'].split('\n')
        for ability in abilities:
            out.append(self.analyze_ability(ability))
        return out

    def analyze_ability(self, text):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        pattern = []
        for token in doc:
            pattern.append((token.text, token.pos_))
        return pattern

if __name__ == "__main__":
    
    parser = SemanticCardParser()
    from card_fetcher import CardsContext

    cards_to_parse = [
        "Acererak the Archlich",
        "Atraxa, Praetors' Voice",
        "Baleful Strix",
        "Aetherworks Marvel",
        "Lair of the Hydra",
        "Baba Lysaga, Night Witch",
        "Chandra, Awakened Inferno",
        "Teferi, Hero of Dominaria",
        "Grixis Charm",
        "Stasis",
        "Sphinx of the Second Sun",
        "Gift of Immortality",
        "Mythos of Nethroi",
        "Terminus",
        "Soulherder",
        "Pact of Negation",
        "Soulfire Grand Master",
        "Soulfire Eruption",
        "Tragic Arrogance",
        "Preordain",
        "Wishclaw Talisman",
        "Wheel of Fortune",
    ]

    db = CardsContext()
    card_data = [db.get_card_by_name(card_name) for card_name in cards_to_parse]

    parsed_data = [parser.parse_card(card) for card in card_data]

    with open("semantic_parsed_data.json", "w") as f:
        json.dump(parsed_data, f, indent=2)