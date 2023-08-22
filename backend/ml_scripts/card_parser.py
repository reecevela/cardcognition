import re
import json
from converter import MLConverter

class CardParser:
    def __init__(self):
        self.properties_dict = {
            #"permanent": ["Creature", "Artifact", "Land", "Enchantment", "Planeswalker", "Battle"],
            #"spell": ["Sorcery", "Instant"],
            "X": ["{X}"],
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
            "0cmc": ["cmc:0"],
            "1cmc": ["cmc:1"],
            "2cmc": ["cmc:2"],
            "mid_cmc": ["cmc:3", "cmc:4"],
            "high_cmc": ["cmc:5", "cmc:6", "cmc:7", "cmc:8"],   
            "very_high_cmc": ["cmc:9", "cmc:10", "cmc:11", "cmc:12", "cmc:13", "cmc:14", "cmc:15", "cmc:16", "cmc:17", "cmc:18", "cmc:19", "cmc:20"],
        }
        self.vanilla_keywords = [
            "Deathtouch", "Defender", "Double strike", "First strike", "Flash", "Flying", "Haste", "Hexproof", "Indestructible", "Lifelink", "Menace", "Reach", "Trample", "Vigilance", "Shroud", "Protection", "Cascade"
        ]
        self.card_features = {
            "alternate_casting": ["without paying its mana cost", ["you may pay", "rather than", "cost"], ["cast this spell for", "rather"], ["your library", "onto the battlefield"]],
            "artifacts_matter": [["for each", "artifact"], ["artifact", "you control"], "artifact card", ["you", "cast", "artifact"], ["an artifact", "enters the battlefield"], ["artifact", "cost", "less to cast"], ["artifacts", "you control", "have"]],
            "aura": ["aura"],
            "damage": [["deal", "damage", "to"]],
            "blink": [["exile target", "return", "to the battlefield"], ["exile CARDNAME", "return", "to the battlefield"], ["exile any number", "return", "to the battlefield"], ["When", ", exile", "until", "leaves the battlefield"]],
            "board_wipe": ["Destroy all", "Exile all", "Destroy each", "Exile each", "Each player sacrifices", ["CARDNAME", "damage", "to each creature"]],
            "bounce": [["return", "target creature", "owner", "hand"], ["return", "target", "it's owner", "hand"], "into it's owner's libary"],
            "card_advantage": ["draw", ["exile the top", "you may play"], "to your hand"],
            "chaos": ["at random", "roll", "dice", "flip", "until you reveal"], # Watching for too many false positives (On the bottom of your library in a random order, etc.)
            "clone": ["as a copy of", ["a token", "copy of target"]],
            "combat_trigger": [["whenever", "attacks"], ["at", "combat main phase"], "deals combat damage", "deals damage to a player", ["when", "you attack"], "becomes blocked", "additional combat", "that attacked", "whenever CARDNAME attacks"],
            "control_effect": ["gain control of", ["from an opponent's", "under your control"], "exchange control"],
            "cost_reducer": [["spells", "cast", "cost", "less"], ["abilities", "cost", "less", "to activate"]],
            "counters": ["counter on", "counters on", "counters among", "proliferate", "Proliferate"],
            "counterspells": ["Counter target", "counter target", "Return target spell", "Put target spell into"],
            "creatures_matter": [["for each", "creature"], ["each creature", "you control"], "creature card", ["you", "cast", "creature"], ["whenever", "a creature", "enters the battlefield"], ["creature", "cost", "less to cast"]],
            "curse": ["curse"],
            "death": ["dies", "sacrifice a", ["whenever", "sacrifice"], "put into a graveyard from the battlefield"],
            "discard": ["discard", ["less than", "cards", "hand"]],
            "enchantments_matter": [["for each", "enchantment"], ["enchantment", "you control"], "enchantment card", ["you", "cast", "enchantment"], ["an enchantment", "enters the battlefield"], ["enchantment", "cost", "less to cast"], ["enchantments", "you control", "have"]],
            "equipment_matter": [["for each", "equipment"], ["equipment", "you control"], "equipment card", ["you cast", "equipment"], ["an equipment", "enters the battlefield"], ["equipment", "cost", "less to cast"], ["for each", "equipment"]],
            "ETB": ["enters the battlefield"],
            "evasion": ["menace", "flying", "unblockable", "can't be blocked", "shadow", "can't block"],
            "forced_attack": ["must attack", "goad"],
            "forced_block": ["must block", "target crature blocks", "must be blocked", ["able to block", "do so"]],
            "giveaway_effect": ["opponent gains control", "exchange control", "give control", ["gains control of target", "you control"]],
            "graveyard_castable": ["Flashback", "Dredge", "Madness", "Aftermath", "Escape", "Retrace", ["cast", "CARDNAME from your graveyard"]],
            "graveyard_matter": [["for each", "in your graveyard"], ["cards in your graveyard", "cost", "less to cast"], ["card in your graveyard", "enters the battlefield"], ["whenever", "your graveyard"], "cards in your graveyard", "in your graveyard have"],
            "hate": [["opponent", "equal to", "that player"], ["opponent", "can't", "cast"], ["opponent", "can't", "play"], ["opponent", "can't", "activate"], ["can't", "be sacrificed"], ["cost", "more to cast"], ["opponent", "control", "enter", "tapped"], ["Whenever an opponent"]],
            "instants_matter": [["for each", "instant"], "instant card", ["you cast", "instant"], ["instant", "copy"], ["instant", "cost", "less to cast"], "instants", "instant spells"],
            "lands_matter": [["for each", "land"], ["land", "you control"], "land card", ["you", "play", "land"], ["land", "enters the battlefield"], ["lands"]],
            "life_gain": ["gain life", "gain X life", "gain 1 life", "gain 2 life", "gain 3 life", "gain 4 life", "gain 5 life", "gain 6 life", "gain 7 life", "gain 8 life", "gain 9 life", "gain 10 life", "life total becomes", "to your life total", "life you gain"],
            "life_loss": ["lose life", "lose X life", "lose 1 life", "lose 2 life", "lose 3 life", "lose 4 life", "lose 5 life", "lose 6 life", "lose 7 life", "lose 8 life", "lose 9 life", "lose 10 life", "lost life", "life lost"],
            "milling": ["Mill", "Surveil", "of your library into your graveyard"],
            "morph": ["morph", "face up", "face down"],
            "opp_discard": [["opponent", "discard"], ["each player", "Discards"], ["exiles", "card", "from their hand"], ["target player", "discard"]],
            "pillowfort": ["can't attack", ["prevent", "damage", "to you"], "prevent all damage", "can attack you", "whenever a creature attacks you", ["whenever", "deals damage to you"], "whenever an opponent attacks you", "you have hexproof", "you have shroud", "you can't be the target", "is reduced by"],
            "planeswalkers_matter": ["for each planeswalker", ["a planeswalker", "you control"], "target planeswalker card", ["you cast", "planeswalker"], ["a planeswalker", "enters the battlefield"], ["planeswalker", "cost", "less to cast"], "planeswalkers"],
            "power_boost": [["gets", "+", "/"], "+1/+1", "+2/+2", "+3/+3", "+4/+4", "+5/+5", "+6/+6", "+7/+7", "+8/+8", "+9/+9", "+10/+10", "+11/+11", "+12/+12", "+13/+13", "+14/+14", "+15/+15", "+16/+16", "+17/+17", "+18/+18", "+19/+19", "+20/+20"],
            "protection": ["Protection from", "hexproof", "shroud", "can't be countered", ["prevent all damage", "to target"], "indestructible", "prevent the next"],
            "ramp": [["your library", "land", "onto the battlefield"], ["land", "from your hand", "onto the battlefield"], ["draw", "play", "additional land"], "Add {C", "Add {W", "Add {U", "Add {B", "Add {R", "Add {G", "Add {X", "Add {1", "Add {2", "Add {3", "Add {4", "Add {5", "of any color"],
            "recursion": ["from your graveyard to your hand", "from your graveyard to the battlefield"],
            "redirect": ["change the target of", "choose new target", ["would be dealt", "instead"]],
            "repeat_trigger": ["whenever"],
            "saga": ["chapter", "Saga", "iii"],
            "sorceries_matter": [["for each", "sorcery"], "target sorcery card", ["you cast", "sorcery"], ["sorcery", "copy"], ["sorcery", "cost", "less to cast"], "sorceries", "sorcery spells"],
            "targeted_interaction": ["destroy target", "exile target", ["opponent sacrifices", "with the", "among"], "counter target", ["return", "target", "owner", "hand"], ["target", "into", "owner's", "library"], ["deals", "damage", "target"]],
            "tokens_matter": [["for each", "token you control"], "target token", ["you cast", "create", "token"], ["a token", "enters the battlefield"], "populate", "convoke", "tokens you control"],
            "trigger_once": ["when "],
            "tutor": ["Search your library for a card", ["reveal", "put", "into", "hand"]],
            "untap": ["untap all", "untap each", "untap that", "untap target", "untap up to", "untap up to", "untap X"],
            "wheel": ["Discard your hand", "Discards their hand, then draws", "Shuffle your hand and graveyard into your library, then draw", "Discard your hand, then draw", "hand into their library, then draw"],
            #"card_draw": ["Draw a card", "Draw cards", "Draw X cards"],
            "tap": ["tap target", "tap up to", "tap X", "tap all", "tap each", "tap that", "tapped"], # Matches untap triggers as well
            "extra_turn": ["extra turn", "additional turn"]
        }
        self.card_feature_exclusions = {
            "bounce": ["your graveyard"],
            "tutor": ["land card", "forest card", "island card", "mountain card", "swamp card", "plains card", "basic land"],
            "planeswalkers_matter": ["trample", "or planeswalker"],
            "targeted_interaction": [["gets", "/-0"], "target opponent", "you control"],
            "lands_matter": [["opponent", "equal to", "that player"], "exile target land", "destroy target land", "exile two target land", "that card is a land card", "destroy all", "nonland"],
            "tap": ["untap"],
            "untap": ["doesn't untap", "stun counter", ["skip", "untap"]],
            "creatures_matter": ["noncreature"],
            "power_boost": ["+1/+1 counter"],
            "pillowfort": ["This creature can't attack"],
            "extra_turn": ["skip"],
            "death": ["age counter"],
            "card_advantage": ["draw a card.", "would draw"],
            "evasion": ["CARDNAME can't block"],
            "artifacts_matter": ["nonartifact"],
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

        if oracle_text is None:
            oracle_text = ""
        first_line = oracle_text.split("\n")[0]
        for keyword in self.vanilla_keywords:
            if keyword in first_line:
                properties.add(keyword.lower())

        types = self.converter.process_type_line(type_line)
        properties.update(set([f"SUP_{t}" for t in types['super_types']]))
        properties.update(set([f"TYP_{t}" for t in types['card_types']]))
        properties.update(set([f"SUB_{t}" for t in types['sub_types']]))

        for key, values in self.properties_dict.items():
            for value in values:
                if type_line is not None and value in type_line:
                    properties.add(key)
                elif mana_cost is not None and value in mana_cost:
                    properties.add(key)
                elif power is not None and value in f"power:{power}":
                    properties.add(key)
                elif toughness is not None and value in f"toughness:{toughness}":
                    properties.add(key)
                elif cmc is not None and value in f"cmc:{cmc}":
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
        
        for key, values in self.card_feature_exclusions.items():
            for value in values:
                if type(value) == str:
                    if value.lower() in oracle_text.lower():
                        properties.discard(key)
                elif type(value) == list:
                    matches = True
                    for v in value:
                        if v.lower() not in oracle_text.lower():
                            matches = False
                    if matches:
                        properties.discard(key)
        
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
    rand_index = random.randint(0, len(cards) - 30)

    parsed_data = [[parser.parse_card(card), card.get('oracle_text')] for card in cards[rand_index:rand_index+30]]
    with open("parsed_data.json", "w") as f:
        json.dump(parsed_data, f, indent=2)