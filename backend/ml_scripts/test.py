from card_embedder import CardEmbedder
from card_fetcher import CardsContext
import json
import os
import datetime
import warnings
import time

import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDRegressor
#from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
import numpy as np


with open('config.json', 'r') as f:
    config = json.load(f)
warnings.filterwarnings("ignore")

startTime = time.time()

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
] # Solely because of Yargle, commanders allow empty oracle text

card_name_map = {card['id']: card['card_name'] for card in cards_raw}
commander_name_map = {commander['card_id']: commander['card_name'] for commander in commanders_raw}

cards = {name: card for name, card in zip(card_name_map.values(), cards_raw)}
commanders = {name: cards[name] for name in commander_name_map.values()}

for i, card in enumerate(cards_raw):
    cards[card['card_name']]['index'] = i
    cards[card['id']] = card['card_name']

for i, commander in enumerate(commanders_raw):
    commanders[commander['card_name']]['index'] = i
    commanders[commander['card_name']]['cards'] = []
    commanders[commander['card_id']] = commander['card_name']

print(f"Cards: {len(cards)}")
print(f"Commanders: {len(commanders)}")

# Avoid mapping embeddings at all costs, each card can be a massive vector
# 500,000 rels, 30,000 cards, 1,900 commanders
# Note - rels are ordered by commander_id ASC
# cmd ordered by card_id ASC
# cards ordered by id ASC

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

print(f"Relations: {len(rels)}")
print(f"Time Elapsed: {time.time() - startTime}")

embedder = CardEmbedder()
embeddings = embedder.embed_cards(cards_raw, testing=False)

for commander_name, commander_data in commanders.items():
    try:
        # print(commander_name, " ", commander_data.get('id'))
        # print(len(commander_data.get('cards', [])))
        if commander_name not in commanders:
            # print(f"Skipping {commander_name} because it's not in the cards list")
            continue
        if len(commander_data.get('cards', 0)) < 100:
            # print(f"Skipping {commander_name} because it has {len(commander_data.get('cards', 0))} cards")
            continue
        X = []
        y = []
        for card in commander_data['cards']:
            # print(card[0]['card_name'], card[1])
            # print(embeddings[card[0].get('index')].shape)
            if card and card[0].get('index', None) is not None:
                X.append(embeddings[card[0]['index']])
                y.append(card[1] / 100)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        commanders[commander_name]['model'] = SGDRegressor(penalty=config["penalty"], alpha=config["alpha"])
        commanders[commander_name]['model'].fit(X_train, y_train)
        commanders[commander_name]['score'] = commanders[commander_name]['model'].score(X_test, y_test)
        # print(f"Score for {commander_name}: {commanders[commander_name]['score']}")
    except Exception as e:
        continue
        #print(f"Error for {commander_name}: {e}")


def generate_batches(batch_size, rels, embeddings, commander_name_map, card_name_map):
    num_samples = len(rels)
    for offset in range(0, num_samples, batch_size):
        batch_rels = rels[offset:offset + batch_size]
        X, y = [], []
        for rel in batch_rels:
            commander_name = commander_name_map.get(rel['commander_id'])
            card_name = card_name_map.get(rel['card_id'])
            if commander_name and card_name:
                commander_idx = commanders[commander_name]['index']
                card_idx = cards[card_name]['index']
                commander_embedding = embeddings[commander_idx]
                card_embedding = embeddings[card_idx]
                X.append(np.concatenate((commander_embedding, card_embedding)).reshape(1, -1))
                y.append(rel['percentage'] / 100)
        X = np.vstack(X)
        yield X, np.array(y)


gen_model = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1, warm_start=True, random_state=42, activation=config['activation'], solver='adam')

# Trained with (commander_embedding, card_embedding) -> frequency
print("Starting gen model training...")
batch_size = len(rels) # // 5
i = 0
done = len(rels) // batch_size
for X_batch, y_batch in generate_batches(batch_size, rels, embeddings, commander_name_map, card_name_map):
    print(f"Batch {i} of {done}")
    gen_model.partial_fit(X_batch, y_batch)
    i += 1

joblib.dump(gen_model, 'gen_model.sav')

# Validation Testing
with open("./validation_set.json", 'r') as file:
    validation_data = json.load(file)

analytics_data = dict()

for card in validation_data:
    card_embedding = embedder.embed_cards([card], testing=True)[0]
    test_commanders = [cmd for cmd in card['test_commanders'] if cmd in commanders]
    commander_indices = [commanders[cmd_name]['index'] for cmd_name in test_commanders]
    commander_embeddings = np.array([embeddings[idx] for idx in commander_indices])
    combined_input = np.hstack([commander_embeddings, np.tile(card_embedding, (len(test_commanders), 1))])
    
    analytics_data[card['card_name']] = dict()
    analytics_data[card['card_name']]['general'] = []

    gen_scores = np.round(gen_model.predict(combined_input).flatten(), 4) * 100
    card_predictions = dict(zip(test_commanders, gen_scores))

    for commander_name in card['test_commanders']:
        if commander_name not in commanders:
            # print(f"Skipping {commander_name} because it's not in the dataset")
            continue
        commander = commanders[commander_name]
        score = round(commander['model'].predict([card_embedding])[0], 4) * 100
        card_predictions[commander_name] = score

        # General model predicts commander + card frequency
        try:
            combined_input = np.concatenate((embeddings[commanders[commander_name]['index']], card_embedding)).reshape(1, -1)
        except Exception as e:
            print(e)
            continue
        gen_score = round(gen_model.predict(combined_input)[0], 4) * 100
        print(f"{commander_name} {card['card_name']} {gen_score}")
        analytics_data[card['card_name']]['general'].append([commander_name, gen_score])

    median = np.median(list(card_predictions.values()))
    correct_list = [(cmd, score) for cmd, score in card_predictions.items() if (score >= median and cmd in card['expected_high']) or (score < median and cmd in card['expected_low'])]
    incorrect_list = [(cmd, score) for cmd, score in card_predictions.items() if (score >= median and cmd not in card['expected_high']) or (score < median and cmd not in card['expected_low'])]

    accuracy = len(correct_list) / (len(correct_list) + len(incorrect_list))
    
    print(f"Accuracy for {card['card_name']}: {accuracy}")
    print(f"Correct: {correct_list}")
    print(f"Incorrect: {incorrect_list}")
    analytics_data[card['card_name']]['accuracy'] = accuracy
    analytics_data[card['card_name']]['correct'] = correct_list
    analytics_data[card['card_name']]['incorrect'] = incorrect_list

    gen_median = np.median([cmd_prediction[1] for cmd_prediction in analytics_data[card['card_name']]['general']])
    gen_correct_list = [cmd_prediction for cmd_prediction in analytics_data[card['card_name']]['general'] if (cmd_prediction[1] >= gen_median and cmd_prediction[0] in card['expected_high']) or (cmd_prediction[1] < gen_median and cmd_prediction[0] in card['expected_low'])]
    gen_incorrect_list = [cmd_prediction for cmd_prediction in analytics_data[card['card_name']]['general'] if (cmd_prediction[1] >= gen_median and cmd_prediction[0] not in card['expected_high']) or (cmd_prediction[1] < gen_median and cmd_prediction[0] not in card['expected_low'])]

    gen_accuracy = len(gen_correct_list) / (len(gen_correct_list) + len(gen_incorrect_list))
    print(f"General Model Accuracy: {gen_accuracy}, {gen_accuracy} / {len(gen_correct_list) + len(gen_incorrect_list)}")
    print(f"General Model Correct: {gen_correct_list}")
    print(f"General Model Incorrect: {gen_incorrect_list}")
    analytics_data[card['card_name']]['general_accuracy'] = gen_accuracy
    analytics_data[card['card_name']]['general_correct'] = gen_correct_list
    analytics_data[card['card_name']]['general_incorrect'] = gen_incorrect_list

average_validation_accuracy = np.mean([analytics_data[card['card_name']]['accuracy'] for card in analytics_data])
print(f"Average validation accuracy: {average_validation_accuracy}")
analytics_data['average_validation_accuracy'] = average_validation_accuracy


average_commander_score = np.mean([commander_data.get('score', 0) for commander_name, commander_data in commanders.items()])
print(f"Average commander score: {average_commander_score}")
analytics_data['average_commander_score'] = average_commander_score

total_time_elapsed = time.time() - startTime
print(f"Total time elapsed: {total_time_elapsed}")
analytics_data['total_time_elapsed'] = total_time_elapsed

if not os.path.exists("analytics"):
    os.makedirs("analytics")

now = datetime.datetime.now()
analytics_file_name = f"analytics/analytics_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
analytics_data["config"] = config

with open(analytics_file_name, 'w') as file:
    json.dump(analytics_data, file, indent=4)
