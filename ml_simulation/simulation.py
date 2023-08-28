import random
from helpers import *
from zones import Zones

print(Zones.HAND)

grave_bolt = {
    "state": "hand",
    "hand": {
        "cost": ["R"],
        "effect": ["damage", "any", 3],
        "resolve": ["graveyard"]
    },
    "graveyard": {
        "cost": [3, "R"],
        "resolve": ["hand"]
    }
}

titanic_might = {
    "state": "hand",
    "hand": {
        "cost": ["G", "G"],
        "effect": ["damage", "any", 10],
        "resolve": ["graveyard"]
    },
}

mana_pool = ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "G", "G", "G", "G"]
cards = [grave_bolt.copy(), grave_bolt.copy(), titanic_might.copy(), titanic_might.copy()]  # Create copies of the original card

damage_dealt = 0
turns = 10

while turns > 0:
    available_actions = []

    for card in cards:
        card_state = card["state"]
        card_data = card.get(card_state, None)

        if card_data is None:
            continue

        if can_pay_cost(mana_pool, card_data["cost"]):
            available_actions.append((card, card_data))

    if len(available_actions) == 0:
        break
    
    print(f"Mana Pool: {mana_pool}")
    action_card, action = random.choice(available_actions)
    print(f"Action: {action}")
    mana_pool = pay_cost(mana_pool, action["cost"])
    print(f"Mana Pool: {mana_pool}")

    if action.get("effect", None) is not None:
        if action["effect"][0] == "damage":
            if action["effect"][1] == "any":
                damage_dealt += action["effect"][2]

    action_card["state"] = action["resolve"][0]
    turns -= 1

print(f"Damage dealt: {damage_dealt}")
