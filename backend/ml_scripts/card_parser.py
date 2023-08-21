import re
import json
from converter import MLConverter

class CardParser:
    def __init__(self):
        self.properties_dict = {
            "permanent": ["Creature", "Artifact", "Land", "Enchantment", "Planeswalker", "Battle"],
            "spell": ["Sorcery", "Instant"],
            "green": ["{G}"],
            "blue": ["{U}"],
            "red": ["{R}"],
            "white": ["{W}"],
            "black": ["{B}"],
            "colorless": ["{C}"],
            "hybrid_mana": [
                "{W/B}", "{W/G}", "{W/U}", "{W/R}",
                "{U/R}", "{U/W}", "{U/B}", "{U/G}",
                "{B/G}", "{B/U}", "{B/R}", "{B/W}",
                "{R/W}", "{R/W}", "{R/B}", "{R/G}",
                "{G/U}", "{G/R}", "{G/W}", "{G/B}", 
            ],
            "0power": ["power:0"],
            "1power": ["power:1"],
            "2power": ["power:2"],
            "mid_power": ["power:3", "power:4"],
            "high_power": ["power:5", "power:6", "power:7", "power:8"],
            "very_high_power": ["power:9", "power:10", "power:11", "power:12", "power:13", "power:14", "power:15", "power:16", "power:17", "power:18", "power:19", "power:20"],
            "0toughness": ["toughness:0"],
            "1toughness": ["toughness:1"],
            "2toughness": ["toughness:2"],
            "mid_toughness": ["toughness:3", "toughness:4"],
            "high_toughness": ["toughness:5", "toughness:6", "toughness:7", "toughness:8"],
            "very_high_toughness": ["toughness:9", "toughness:10", "toughness:11", "toughness:12", "toughness:13", "toughness:14", "toughness:15", "toughness:16", "toughness:17", "toughness:18", "toughness:19", "toughness:20"], 
        }
        self.vanilla_keywords = [
            "Deathtouch", "Defender", "Double strike", "First strike", "Flash", "Flying", "Haste", "Hexproof", "Indestructible", "Lifelink", "Menace", "Reach", "Trample", "Vigilance", "Shroud", "Protection",
        ]
        self.card_features = {
            "graveyard_castable": ["Flashback", "Dredge", "Madness", "Aftermath", "Escape", "Retrace", ["cast", "CARDNAME from your graveyard"]],
            "milling": ["Mill", "Surveil", "of your library into your graveyard"],
            "board_wipe": ["Destroy all", "Exile all", "Destroy each", "Exile each", "Each player sacrifices", ["CARDNAME", "damage", "to each"]],
            "card_draw": ["Draw a card", "Draw cards", "Draw X cards"],
            "card_advantage": ["draw", ["exile the top", "you may play"], "to your hand"],
            "wheel": ["Discard your hand", "Discards their hand, then draws", "Shuffle your hand and graveyard into your library, then draw", "Discard your hand, then draw", "hand into their library, then draw"],
            "opp_discard": [["opponent", "discard"], ["each player", "Discards"], ["exiles", "card", "from their hand"], ["target player", "discard"]],
            "discard": ["discard", ["less than", "cards", "hand"]],
            "ramp": [["your library", "land", "onto the battlefield"], ["land", "from your hand", "onto the battlefield"], ["draw", "play", "additional land"], "Add {C", "Add {W", "Add {U", "Add {B", "Add {R", "Add {G", "Add {X", "Add {1", "Add {2", "Add {3", "Add {4", "Add {5", "of any color"],
            "death": ["dies", "sacrifice a", ["whenever", "sacrifice"], "put into a graveyard from the battlefield"],
            "life_gain": ["gain life", "gain X life", "gain 1 life", "gain 2 life", "gain 3 life", "gain 4 life", "gain 5 life", "gain 6 life", "gain 7 life", "gain 8 life", "gain 9 life", "gain 10 life", "life total becomes", "to your life total", "life you gain"],
            "life_loss": ["lose life", "lose X life", "lose 1 life", "lose 2 life", "lose 3 life", "lose 4 life", "lose 5 life", "lose 6 life", "lose 7 life", "lose 8 life", "lose 9 life", "lose 10 life", "lost life", "life lost"],
            "counters": ["counter on", "counters on", "counters among", "proliferate", "Proliferate"],
            "counterspells": ["Counter target", "counter target", "Return target spell", "Put target spell into"],
            "bounce": ["return target", "Return target", "into it's owner's libary"],
            "recursion": ["from your graveyard to your hand", "from your graveyard to the battlefield"],
            "tutor": ["Search your library for a card", ["reveal", "put", "into", "hand"]],
            "protection": ["Protection from", "hexproof", "shroud", "can't be countered", ["prevent all damage", "to target"], "indestructible"],
            "aggressive_combat": [["whenever", "attacks"], "combat phase", "deals combat damage", "attacking", "you attack", ["can't", "block"]],
            "targeted_interaction": ["destroy target", "exile target", ["opponent sacrifices", "with the", "among"], "counter target", "return target", ["target", "into", "owner's", "library"]],
            "untap": ["untap all", "untap each", "untap that", "untap target", "untap up to", "untap up to", "untap X", "untapped"],
            "tap": ["tap target", "tap up to", "tap X", "tap all", "tap each", "tap that", "tapped"],
            "alternate_casting": ["without paying its mana cost", ["you may pay", "rather than", "cost"], ["cast this spell for", "rather"]],
            "enchantments_matter": [["for each", "enchantment"], ["enchantment", "you control"], "enchantment card", ["you", "cast", "enchantment"], ["an enchantment", "enters the battlefield"], ["enchantment", "cost", "less to cast"], ["enchantments", "you control", "have"]],
            "artifacts_matter": [["for each", "artifact"], ["artifact", "you control"], "artifact card", ["you", "cast", "artifact"], ["an artifact", "enters the battlefield"], ["artifact", "cost", "less to cast"], ["artifacts", "you control", "have"]],
            "lands_matter": [["for each", "land"], ["land", "you control"], "land card", ["you", "play", "land"], ["land", "enters the battlefield"], ["lands"]],
            "creatures_matter": [["for each", "creature"], ["each creature", "you control"], "creature card", ["you", "cast", "creature"], ["a creature", "enters the battlefield"], ["creature", "cost", "less to cast"]],
            "instants_matter": [["for each", "instant"], "instant card", ["you cast", "instant"], ["instant", "copy"], ["instant", "cost", "less to cast"], "instants", "instant spells"],
            "sorceries_matter": [["for each", "sorcery"], "sorcery card", ["you cast", "sorcery"], ["sorcery", "copy"], ["sorcery", "cost", "less to cast"], "sorceries", "sorcery spells"],
            "planeswalkers_matter": [["for each", "planeswalker"], ["planeswalker", "you control"], "planeswalker card", ["you cast", "planeswalker"], ["a planeswalker", "enters the battlefield"], ["planeswalker", "cost", "less to cast"], "planeswalkers"],
            "graveyard_matter": [["for each", "in your graveyard"], ["cards in your graveyard", "cost", "less to cast"], ["card in your graveyard", "enters the battlefield"], ["whenever", "your graveyard"], "cards in your graveyard", "in your graveyard have"],
            "tokens_matter": [["for each", "token you control"], "target token", ["you cast", "token"], ["a token", "enters the battlefield"], "populate", "convoke", "tokens you control"],
            "control_effect": ["gain control of", ["from an opponent's", "under your control"], "exchange control"],
            "giveaway_effect": ["opponent gains control", "exchange control", "give control", ["gains control of target", "you control"]],
            "equipment_matter": [["for each", "equipment"], ["equipment", "you control"], "equipment card", ["you cast", "equipment"], ["an equipment", "enters the battlefield"], ["equipment", "cost", "less to cast"], ["for each", "equipment"]],
            "pillowfort": ["can't attack", ["prevent", "damage", "to you"], "prevent all damage", "can attack you", "whenever a creature attacks you", ["whenever", "deals damage to you"], "whenever an opponent attacks you", "you have hexproof", "you have shroud", "you can't be the target"],
            "blink": [["exile", "return", "to the battlefield"]],
            "hate": [["can't", "cast"], ["can't", "play"], ["can't", "activate"], ["can't", "be sacrificed"], ["cost", "more to cast"], ["opponent", "enter", "tapped"], ["Whenever an opponent"]],
            "clone": ["as a copy of", ["a token", "copy of target"], ]
        }
        self.initial_verbs = [
            "Search", "Choose", "Put", "Create", "Return", "Destroy", "Exile", "Sacrifice", "Discard", "Tap", "Untap", "Gain", "Lose", "Draw", "Shuffle", "Scry", "Reveal", "Counter", "You may", "Roll", "Each", "Target", "CARDNAME deals", "Return", "Add", "Each opponen"
        ]
        self.converter = MLConverter()
    
    def parse_abilities(self, oracle_text):
        abilities = []
        if oracle_text is None:
            return abilities
        # Remove reminder text in parentheses
        oracle_text = re.sub(r"\([^)]+\)", "", oracle_text)
        ability_parts = oracle_text.split("\n")
        for part in ability_parts:
            costs, _, effects = part.partition(":")
            costs = re.findall(r"\{[^\}]+\}", costs)
            if costs and effects:
                effects_list = [effect.strip() for effect in effects.split(".")]
                effects_list = [effect for effect in effects_list if effect != "" and effect != " "]
                abilities.append([costs, effects_list])
        return abilities
    
    def parse_effects(self, oracle_text, type_line:None):
        effects = []

        if oracle_text is None:
            return effects

        # Remove reminder text in parentheses
        oracle_text = re.sub(r"\([^)]+\)", "", oracle_text)

        if oracle_text is None:
            return effects

        if 'Instant' in type_line or 'Sorcery' in type_line:
            if "—" in type_line:
                type_line = type_line.split('—')[1]
            effects = oracle_text.split('\n')
            effects = [["CAST", effect.strip()] for effect in effects if effect != "" and effect != " "]
            return effects

        # Replace "At...," phrases with "OPT,"
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
                effects.append([condition, effect])

        return effects
    
    def parse_properties(self, card):
        properties = set()

        oracle_text = card.get("oracle_text", "")
        type_line = card.get("type_line", "")
        mana_cost = card.get("mana_cost", "")
        power = card.get("power", "")
        toughness = card.get("toughness", "")
        cmc = card.get("cmc", "")

        first_line = oracle_text.split("\n")[0]
        for keyword in self.vanilla_keywords:
            if keyword in first_line:
                properties.add(keyword.lower())

        types = self.converter.process_type_line(type_line)
        properties.update(set(types['super_types']))
        properties.update(set(types['card_types']))
        properties.update(set(types['sub_types']))

        properties.add("cmc:" + str(cmc))

        for key, values in self.properties_dict.items():
            for value in values:
                if value in type_line or value in mana_cost or value in f"power:{power}" or value in f"toughness:{toughness}":
                    properties.add(key)
        for key, values in self.card_features.items():
            for value in values:
                if type(value) == str:
                    if value.lower() in oracle_text.lower():
                        properties.add(key)
                elif type(value) == list:
                    matches = True
                    for v in value:
                        if v.lower() not in oracle_text.lower():
                            matches = False
                    if matches:
                        properties.add(key)
        
        return list(properties)
    
    def parse_card(self, card):
        abilities = self.parse_abilities(card.get("oracle_text", ""))
        effects = self.parse_effects(card.get("oracle_text", ""), card.get("type_line", ""))
        properties = self.parse_properties(card)
        return {"name": card.get('card_name'), "abilities": abilities, "effects": effects, "properties": properties}

if __name__ == "__main__":
    
    parser = CardParser()

    card_data = [
        {
            "card_name": "Aetherworks Marvel",
            "oracle_text": "Whenever a permanent you control is put into a graveyard, you get {E} (an energy counter).\n{T}, Pay {E}{E}{E}{E}{E}{E}: Look at the top six cards of your library. You may cast a spell from among them without paying its mana cost. Put the rest on the bottom of your library in a random order.",
            "cmc": 4,
            "mana_cost": "{4}",
            "type_line": "Legendary Artifact"
        },
        {
            "card_name": "Cancel",
            "oracle_text": "Counter target spell.",
            "type_line": "Instant",
            "cmc": 3,
            "mana_cost": "{1}{U}{U}"
        },
        {
            "card_name": "Lair of the Hydra",
            "oracle_text": "If you control two or more other lands, CARDNAME enters the battlefield tapped.\n{T}: Add {G}.\n{X}{G}: Until end of turn, CARDNAME becomes an X/X green Hydra creature. It's still a land. X can't be 0.",
            "type_line": "Land — Forest",
            "cmc": 0,
            "mana_cost": ""
        },
        {
            "card_name": "Phyrexian Arena",
            "oracle_text": "At the beginning of your upkeep, you draw a card and you lose 1 life.",
            "type_line": "Enchantment",
            "cmc": 3,
            "mana_cost": "{1}{B}{B}"
        }
    ]

    parsed_data = [parser.parse_card(card) for card in card_data]
    print(json.dumps(parsed_data, indent=4))

    from card_fetcher import CardsContext
    import random
    db = CardsContext()
    cards = db.get_all_cards()
    rand_index = random.randint(0, len(cards) - 10)

    parsed_data = [parser.parse_card(card) for card in cards[rand_index:rand_index+10]]
    with open("parsed_data.json", "w") as f:
        json.dump(parsed_data, f, indent=2)