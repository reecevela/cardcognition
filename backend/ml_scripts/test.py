from card_embedder import CardEmbedder
from card_fetcher import CardsContext
import json
import os
import datetime

from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDRegressor
import numpy as np

with open('config.json', 'r') as f:
    config = json.load(f)

db = CardsContext()

cards_raw = db.get_all_cards()
commanders_raw = db.get_card_ids_of_commanders()
rels = db.get_cmd_pct_relations()

cards_raw = [
    card for card in cards_raw 
    if card['card_name'] is not None
    and card['type_line'] is not None
    and card['oracle_text'] is not None
    and '//' not in card['card_name'] 
    and '//' not in card['type_line'] 
]

commanders_raw = [
    commander for commander in commanders_raw 
    if '//' not in commander['card_name'] 
] # Solely because of Yargle, empty oracle text is allowed

card_name_map = {card['id']: card['card_name'] for card in cards_raw}
commander_name_map = {commander['card_id']: commander['card_name'] for commander in commanders_raw}

cards = {name: card for name, card in zip(card_name_map.values(), cards_raw)}
commanders = {name: cards[name] for name in commander_name_map.values()}

for i, card in enumerate(cards_raw):
    cards[card['card_name']] = card
    cards[card['card_name']]['index'] = i
    # This acts as a pointer to the card that
    # the rels can reference
    cards[card['id']] = card['card_name']

for i, commander in enumerate(commanders_raw):
    commanders[commander['card_name']] = cards[commander['card_name']]
    commanders[commander['card_name']]['index'] = i
    commanders[commander['card_name']]['cards'] = []
    # This acts as a pointer to the commander for rels
    commanders[commander['card_id']] = commander['card_name']

print(f"Cards: {len(cards)}")
print(f"Commanders: {len(commanders)}")
# Mapping rels to cards/commanders would be nice but a major performance bottleneck
# 500,000 rels, 30,000 cards, 1,900 commanders
# Note - rels are ordered by commander_id ASC
# cmd ordered by card_id ASC
# cards ordered by id ASC
# But rather than doing nested binary searches for each, we can just iterate once.

for rel in rels:
    commander_name = commander_name_map.get(rel['commander_id'])
    card_name = card_name_map.get(rel['card_id'])
    if commander_name and card_name:
        commanders[commander_name]['cards'].append(
            (
                cards[card_name],
                rel['percentage'],
                rel['synergy_score']
            )
        )

embedder = CardEmbedder()
embeddings = embedder.embed_cards(cards_raw, testing=False)

for commander_name, commander_data in commanders.items():
    print(commander_name, " ", commander_data['id'])
    print(len(commander_data['cards']))
    if commander_name not in commanders:
        print(f"Skipping {commander_name} because it's not in the cards list")
        continue
    if len(commander_data['cards']) < 100:
        print(f"Skipping {commander_name} because it has {len(commander_data['cards'])} cards")
        continue
    X = []
    y = []
    for card in commander_data['cards']:
        print(card[0]['card_name'], card[1])
        print(embeddings[card[0]['index']].shape)
        if card:
            X.append(embeddings[card[0]['index']])
            y.append(card[1])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    commanders[commander_name]['model'] = SGDRegressor(penalty=config["penalty"], alpha=config["alpha"])
    commanders[commander_name]['model'].fit(X_train, y_train)
    commanders[commander_name]['score'] = commanders[commander_name]['model'].score(X_test, y_test)

    print(f"Score for {commander_name}: {commanders[commander_name]['score']}")

with open("./validation_set.json", 'r') as file:
    validation_data = json.load(file)

analytics_data = dict()

for card in validation_data:
    card_embedding = embedder.embed_cards([card], testing=True)[0]
    card_predictions = dict()
    analytics_data[card['card_name']] = dict()

    for commander_name in card['test_commanders']:
        if commander_name not in commanders:
            print(f"Skipping {commander_name} because it's not in the dataset")
            continue
        commander = commanders[commander_name]
        score = commander['model'].predict([card_embedding])[0]
        card_predictions[commander_name] = score

    median = np.median(list(card_predictions.values()))
    correct_list = []
    incorrect_list = []
    for commander_name in card_predictions:
        if card_predictions[commander_name] >= median:
            correct_list.append((commander_name, card_predictions[commander_name]))
        else:
            incorrect_list.append((commander_name, card_predictions[commander_name]))
    accuracy = len(correct_list) / (len(correct_list) + len(incorrect_list))
    print(f"Accuracy for {card['card_name']}: {accuracy}")
    print(f"Correct: {correct_list}")
    print(f"Incorrect: {incorrect_list}")
    analytics_data[card['card_name']]['accuracy'] = accuracy
    analytics_data[card['card_name']]['correct'] = correct_list
    analytics_data[card['card_name']]['incorrect'] = incorrect_list

if not os.path.exists("analytics"):
    os.makedirs("analytics")

now = datetime.datetime.now()
analytics_file_name = f"analytics/analytics_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
analytics_data["config"] = config

with open(analytics_file_name, 'w') as file:
    json.dump(analytics_data, file, indent=4)
