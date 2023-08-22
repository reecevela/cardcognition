from card_embedder import CardEmbedder
from card_fetcher import CardsContext
from converter import MLConverter
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
converter = MLConverter()

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

# print(f"Cards: {len(cards)}")
# print(f"Commanders: {len(commanders)}")

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
        if 'highest_score' not in commanders[commander_name] or commanders[commander_name]['highest_score'] < rel['percentage']:
            commanders[commander_name]['highest_score'] = rel['percentage']
        if 'lowest_score' not in commanders[commander_name] or commanders[commander_name]['lowest_score'] > rel['percentage']:
            commanders[commander_name]['lowest_score'] = rel['percentage']

# print(f"Relations: {len(rels)}")
print(f"Time Elapsed: {time.time() - startTime}")

embedder = CardEmbedder()
embeddings = embedder.embed_and_parse_cards(cards_raw) #, testing=False)
joblib.dump(embeddings, 'embeddings.npy')
print(f"Time Elapsed: {time.time() - startTime}")

i = 0
for commander_name, commander_data in commanders.items():
    i += 1
    if i % 100 == 0:
        print(f"Training model {i} of {len(commanders)}")
    try:
        # print(commander_name, " ", commander_data.get('id'))
        # print(len(commander_data.get('cards', [])))
        if commander_name not in commanders:
            # print(f"Skipping {commander_name} because it's not in the cards list")
            continue
        if len(commander_data.get('cards', 0)) < 130:
            # print(f"Skipping {commander_name} because it has {len(commander_data.get('cards', 0))} cards")
            continue
        X = []
        y = []
        highest_card_score = commander_data['highest_score']
        lowest_card_score = commander_data['lowest_score']
        for card in commander_data['cards']:
            # print(card[0]['card_name'], card[1])
            # print(embeddings[card[0].get('index')].shape)
            if card and card[0].get('index', None) is not None:
                X.append(embeddings[card[0]['index']])
                # Normalizes the score, so some commanders aren't skewed to the top when ranked later
                y.append( card[1] - lowest_card_score / (highest_card_score - lowest_card_score) )
                # y.append(card[1] / 100)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        commanders[commander_name]['model'] = SGDRegressor(penalty=config["penalty"], alpha=config["alpha"])
        commanders[commander_name]['model'].fit(X_train, y_train)
        commanders[commander_name]['score'] = commanders[commander_name]['model'].score(X_test, y_test)
        # print(f"Score for {commander_name}: {commanders[commander_name]['score']}")
        # Save model
        cmd_file_name = converter.sanitize_filename(commander_name)
        # print(f"Saving model for {commander_name} to {cmd_file_name}")
        joblib.dump(commanders[commander_name]['model'], f"cmd_models/{cmd_file_name}.joblib")
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
                cmd_high = commanders[commander_name].get('highest_score', None)
                cmd_low = commanders[commander_name].get('lowest_score', None)
                if cmd_high is None or cmd_low is None:
                    continue
                commander_embedding = embeddings[commander_idx]
                card_embedding = embeddings[card_idx]
                X.append(np.concatenate((commander_embedding, card_embedding)).reshape(1, -1))
                y.append(rel['percentage'] - cmd_low / (cmd_high + 1 - cmd_low))
        X = np.vstack(X)
        yield X, np.array(y)


gen_model = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1, warm_start=True, random_state=42, activation=config['activation'], solver='adam')
#gen_model = SGDRegressor(penalty=config["penalty"], alpha=config["alpha"], warm_start=True, random_state=42)
#gen_model = XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)

# Trained with (commander_embedding, card_embedding) -> frequency
print("Starting gen model training...")
print("Time Elapsed: ", time.time() - startTime)
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
    card_embedding = embedder.embed_and_parse_cards([card], testing=True)[0]
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
        # print(f"{commander_name} {card['card_name']} {gen_score}")
        analytics_data[card['card_name']]['general'].append([commander_name, gen_score])

    try:
        median = np.median(list(card_predictions.values()))
        correct_list = [(cmd, score) for cmd, score in card_predictions.items() if (score >= median and cmd in card['expected_high']) or (score < median and cmd in card['expected_low'])]
        incorrect_list = [(cmd, score) for cmd, score in card_predictions.items() if (score >= median and cmd not in card['expected_high']) or (score < median and cmd not in card['expected_low'])]

        accuracy = len(correct_list) / (len(correct_list) + len(incorrect_list))
        
        # print(f"Accuracy for {card['card_name']}: {accuracy}")
        # print(f"Correct: {correct_list}")
        # print(f"Incorrect: {incorrect_list}")
        analytics_data[card['card_name']]['accuracy'] = accuracy
        analytics_data[card['card_name']]['correct'] = correct_list
        analytics_data[card['card_name']]['incorrect'] = incorrect_list
    except Exception as e:
        print(e)
    try:
        gen_median = np.median([cmd_prediction[1] for cmd_prediction in analytics_data[card['card_name']]['general']])
        gen_correct_list = [cmd_prediction for cmd_prediction in analytics_data[card['card_name']]['general'] if (cmd_prediction[1] >= gen_median and cmd_prediction[0] in card['expected_high']) or (cmd_prediction[1] < gen_median and cmd_prediction[0] in card['expected_low'])]
        gen_incorrect_list = [cmd_prediction for cmd_prediction in analytics_data[card['card_name']]['general'] if (cmd_prediction[1] >= gen_median and cmd_prediction[0] not in card['expected_high']) or (cmd_prediction[1] < gen_median and cmd_prediction[0] not in card['expected_low'])]

        gen_accuracy = len(gen_correct_list) / (len(gen_correct_list) + len(gen_incorrect_list))
        # print(f"General Model Accuracy: {gen_accuracy}, {gen_accuracy} / {len(gen_correct_list) + len(gen_incorrect_list)}")
        # print(f"General Model Correct: {gen_correct_list}")
        # print(f"General Model Incorrect: {gen_incorrect_list}")
        analytics_data[card['card_name']]['general_accuracy'] = gen_accuracy
        analytics_data[card['card_name']]['general_correct'] = gen_correct_list
        analytics_data[card['card_name']]['general_incorrect'] = gen_incorrect_list
    except Exception as e:
        print(e)

try:
    average_validation_accuracy = np.mean([data['accuracy'] for card_name, data in analytics_data.items()])
    print(f"Average validation accuracy: {average_validation_accuracy}")
    analytics_data['average_validation_accuracy'] = average_validation_accuracy
except Exception as e:
    print(e)
try:
    average_general_accuracy = np.mean([data['general_accuracy'] for card_name, data in analytics_data.items()])
    print(f"Average general model accuracy: {average_general_accuracy}")
    analytics_data['average_general_accuracy'] = average_general_accuracy
except Exception as e:
    print(e)
try:
    sum = 0
    count = 0
    for commander_name, commander_data in commanders.items():
        try:
            commander_data['score'] = np.round(commander_data['score'], 4) * 100
            sum += commander_data['score']
            count += 1
        except:
            continue
    average_score = sum / count
    print(f"Average score: {average_score}")
    analytics_data['average_cmd_model_score'] = average_score
except Exception as e:
    print(e)
try:
    total_time_elapsed = time.time() - startTime
    print(f"Total time elapsed: {total_time_elapsed}")
    analytics_data['total_time_elapsed'] = total_time_elapsed
except Exception as e:
    print(e)

if not os.path.exists("analytics"):
    os.makedirs("analytics")

now = datetime.datetime.now()
analytics_file_name = f"analytics/analytics_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
analytics_data["config"] = config

with open(analytics_file_name, 'w') as file:
    json.dump(analytics_data, file, indent=4)
