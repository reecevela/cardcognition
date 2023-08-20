import re
import json
from converter import MLConverter

class CardParser:
    def __init__(self):
        self.properties_dict = {
            "land": ["Land"],
            "forest": ["Forest"],
            "permanent": ["Creature", "Artifact", "Land", "Enchantment"],
            "green": ["{G}"],
            "instant": ["Instant"],
            "spell": ["Sorcery", "Instant"],
            "blue": ["{U}"],
            "legendary": ["Legendary"],
            "artifact": ["Artifact"],
        }
        self.converter = MLConverter()
    
    def parse_abilities(self, oracle_text):
        abilities = []
        ability_parts = oracle_text.split("\n")
        for part in ability_parts:
            costs, _, effects = part.partition(":")
            costs = re.findall(r"\{[^\}]+\}", costs)
            if costs and effects:
                effects_list = [effect.strip() for effect in effects.split(".")]
                effects_list = [effect for effect in effects_list if effect != "" and effect != " "]
                abilities.append([costs, effects_list])
        return abilities
    
    def parse_effects(self, oracle_text):
        effects = {}

        # Replace "At..." phrases with "OPT,"
        oracle_text = re.sub(r"At [^,]+,", "OPT,", oracle_text)

        # Define patterns that indicate a triggered effect
        patterns = [
            (r"Whenever ([^\.]+), ([^\.]+)\.", 2),
            (r"When ([^\.]+), ([^\.]+)\.", 2),
            (r"OPT, ([^\.]+)\.", 1)
        ]

        for pattern, group_count in patterns:
            matches = re.findall(pattern, oracle_text)
            for match in matches:
                if group_count == 2:
                    condition, effect = match
                elif group_count == 1:
                    condition = "OPT"
                    effect = match
                effect_descriptor = condition
                effects[effect_descriptor] = effect

        return effects
    
    def parse_properties(self, type_line, mana_cost):
        properties = set()
        types = self.converter.process_type_line(type_line)
        properties.update(set(types['super_types']))
        properties.update(set(types['card_types']))
        properties.update(set(types['sub_types']))
        for key, values in self.properties_dict.items():
            for value in values:
                if value in type_line or value in mana_cost:
                    properties.add(key)
        return list(properties)
    
    def parse_card(self, card):
        abilities = self.parse_abilities(card.get("oracle_text", ""))
        effects = self.parse_effects(card.get("oracle_text", ""))
        properties = self.parse_properties(card.get("type_line", ""), card.get("mana_cost", ""))
        return {"abilities": abilities, "effects": effects, "properties": properties}

parser = CardParser()

card_data = [
    {
        "oracle_text": "Whenever a permanent you control is put into a graveyard, you get {E} (an energy counter).\n{T}, Pay {E}{E}{E}{E}{E}{E}: Look at the top six cards of your library. You may cast a spell from among them without paying its mana cost. Put the rest on the bottom of your library in a random order.",
        "cmc": 4,
        "mana_cost": "{4}",
        "type_line": "Legendary Artifact"
    },
    {
        "oracle_text": "Counter target spell.",
        "type_line": "Instant",
        "cmc": 3,
        "mana_cost": "{1}{U}{U}"
    },
    {
        "oracle_text": "If you control two or more other lands, CARDNAME enters the battlefield tapped.\n{T}: Add {G}.\n{X}{G}: Until end of turn, CARDNAME becomes an X/X green Hydra creature. It's still a land. X can't be 0.",
        "type_line": "Land — Forest",
        "cmc": 0,
        "mana_cost": ""
    },
    {
        "oracle_text": "At the beginning of your upkeep, you draw a card and you lose 1 life.",
        "type_line": "Enchantment",
        "cmc": 3,
        "mana_cost": "{1}{B}{B}"
    },
    {
        "oracle_text": "CARDNAME enters the battlefield tapped.\n{T}: Add {C}.\n{T}, Pay 1 life: Add {B} or {R}.",
        "type_line": "Land",
        "cmc": 0,
        "mana_cost": ""
    }
]

parsed_data = [parser.parse_card(card) for card in card_data]
print(json.dumps(parsed_data, indent=4))