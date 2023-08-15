from card_embedder import CardEmbedder
from card_fetcher import CardsContext
from converter import MLConverter
import numpy as np
import pickle
import json
import threading
from sklearn.linear_model import Ridge, SGDRegressor
from sklearn.model_selection import train_test_split
import time
from sklearn.utils import shuffle
import os
import datetime
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load config.json
with open("config.json", "r") as f:
    config = json.load(f)

card_id_to_index = {}
commander_id_to_index = {}

# Load previously saved mappings and embeddings
with open('card_id_to_index.pkl', 'rb') as f:
    card_id_to_index = pickle.load(f)
with open('commander_id_to_index.pkl', 'rb') as f:
    commander_id_to_index = pickle.load(f)

card_embeddings = np.load("card_embeddings.npy", allow_pickle=True)
commander_embeddings = np.load("commander_embeddings.npy", allow_pickle=True)

# Get all cards and commanders
context = CardsContext()
cards = context.get_all_cards()
commanders = context.get_commanders()

# Filter out split cards
cards = [card for card in cards if '//' not in card['card_name']]
commanders = [commander for commander in commanders if '//' not in commander['card_name']]

print("Mapping individual commanders...")
commander_to_cards = {}
for commander_card_id in commander_id_to_index:
    if len(commander_to_cards) % 100 == 0:
        print(f"Commanders mapped: {len(commander_to_cards)} out of {len(commander_id_to_index)}, {round(len(commander_to_cards) / len(commander_id_to_index) * 100, 2)}%")
    try:
        commander_id = context.get_cmd_id_from_sc_id(commander_card_id)
        frequencies = context.get_commander_frequencies_by_id(commander_id)
        commander_to_cards[commander_card_id] = frequencies
    except Exception as e:
        print(e)
        continue

# commanders_to_cards is structured like this: 
# {
#   '1712': [{'card_id': 31020, 'percentage': 16}, {'card_id': 31073, 'percentage': 13}],
#   '1713': [{'card_id': 31020, 'percentage': 16}, {'card_id': 31073, 'percentage': 13}],
# ...
# }

individual_commander_models = {}
e_count = 0
for commander_card_id, card_data in commander_to_cards.items():
    print(f"Creating model for {commander_card_id}")
    # Removes invalid cards
    i = 0
    removed_count = 0
    while i < len(card_data):
        if card_data[i]['card_id'] not in card_id_to_index:
            card_data.pop(i)
            removed_count += 1
            continue
        i += 1
    print(f"Removed {removed_count} invalid cards")
    if len(card_data) < 100:
        print(f"Commander {commander_card_id} has {len(card_data)} valid cards, skipping...")
        continue
    X = [card_embeddings[card_id_to_index[card['card_id']]] for card in card_data]
    y = [card['percentage'] for card in card_data]
    model = SGDRegressor(penalty=config['penalty'],alpha=config['alpha']).fit(X, y)
    individual_commander_models[commander_card_id] = model
    print(f"Model for {commander_card_id} created with score: {model.score(X, y)} on {len(X)} examples")



start_time = time.time()
total_commanders = len(commanders)
# Construct examples
gen_cc_examples = []
gen_examples = []
i = 0
j = 0
print("Constructing examples...")
for commander_card_id in commander_id_to_index:
    # Commander's scryfall_cards id
    commander_id = context.get_cmd_id_from_sc_id(commander_card_id)
    # embedding for the actual card itself
    commander_embedding = card_embeddings[card_id_to_index[commander_card_id]]

    synergies = context.get_commander_frequencies_by_id(commander_id)
    for card in synergies:
        i += 1
        card_id = card['card_id']
        frequency = card['percentage']
        try:
            card_embedding = card_embeddings[card_id_to_index[card_id]]
        except Exception as e:
            continue
        gen_cc_examples.append((commander_embedding, card_embedding, frequency))
        gen_examples.append((card_embedding, frequency))
    j += 1
    if j % 100 == 0:
        elapsed_time = time.time() - start_time
        progress = (j+1) / total_commanders
        remaining_time = elapsed_time * (1-progress) / progress
        print(f"Progress: {progress*100:.2f}%, Time remaining: {remaining_time:.2f}s Loss Percent: {(len(gen_cc_examples) - i)/(i+0.001)*100:.2f}% Loss Count: {len(gen_cc_examples) - i} Time elapsed: {elapsed_time:.2f}s")

print("Starting training...")

# Have to do this otherwise the amount of memory crashes my laptop
def generate_batches(batch_size, examples, concat=True):
    while True:
        examples = shuffle(examples)
        for i in range(0, len(examples), batch_size):
            if concat:
                batch_X = [np.concatenate((example[0], example[1])) for example in examples[i:i+batch_size]]
                batch_y = [example[2] for example in examples[i:i+batch_size]]
            else:
                batch_X = [example[0] for example in examples[i:i+batch_size]]
                batch_y = [example[1] for example in examples[i:i+batch_size]]

            yield np.array(batch_X), np.array(batch_y)

print("Splitting data...")
# Combine enbeddings and split data (without storing X and y in memory)
gen_cc_train_examples, gen_cc_test_examples = train_test_split(gen_cc_examples, test_size=0.2, train_size=0.8)
gen_train_examples, gen_test_examples = train_test_split(gen_examples, test_size=0.2, train_size=0.8)

batch_size = config['batch_size']
print("Generating training batches...")
gen_cc_train_batches = generate_batches(batch_size, gen_cc_train_examples, concat=True)
gen_train_batches = generate_batches(batch_size, gen_train_examples, concat=False)
print("Generating testing batches...")
gen_cc_test_batches = generate_batches(batch_size, gen_cc_test_examples, concat=True)
gen_test_batches = generate_batches(batch_size, gen_test_examples, concat=False)

general_cc_model = SGDRegressor(penalty=config["penalty"], alpha=config["alpha"])
general_model = SGDRegressor(penalty=config["penalty"], alpha=config["alpha"])

# Train the General CC model using partial_fit
for i in range(0, len(gen_cc_train_examples), batch_size):
    print("Training batch", i, "of", len(gen_cc_train_examples))
    batch_X, batch_y = next(gen_cc_train_batches)
    general_cc_model.partial_fit(batch_X, batch_y)

# Train the General model using partial_fit
for i in range(0, len(gen_train_examples), batch_size):
    print("Training batch", i, "of", len(gen_train_examples))
    batch_X, batch_y = next(gen_train_batches)
    general_model.partial_fit(batch_X, batch_y)

# Evaluate the General CC model
X_test, y_test = next(gen_cc_test_batches)
cc_score = general_cc_model.score(X_test, y_test)
print('General CC Model R^2 Score:', cc_score)

# Evaluate the General model
X_test, y_test = next(gen_test_batches)
score = general_model.score(X_test, y_test)
print('General Model R^2 Score:', score)

# Validate some fake/custom cards

with open("./validation_set.json", 'r') as file:
    validation_data = json.load(file)

analytics_data = {"score": score}
analytics_data = {"cc_score": cc_score}
analytics_data["config"] = config
accuracy_scores = []
alt_accuracy_scores = []

converter = CardEmbedder()
# Iterate through validation data
for card in validation_data:
    card_name = card['card_name']
    card_embedding = converter.embed_cards([card]).reshape(-1)
    print(card_name)
    analytics_data[card_name] = {}
    predicted_synergy_scores = []
    cc_predicted_synergy_scores = []

    for commander_name in card['test_commanders']:
        commander_id = context.get_id_by_name(commander_name)[0]['id']
        commander_embedding = np.array(card_embeddings[card_id_to_index[commander_id]]).reshape(-1,)

        # Combine embeddings and predict synergy score
        new_pair_embedding = np.concatenate((commander_embedding, card_embedding)).reshape(1, -1)
        individual_pred = individual_commander_models[commander_id].predict(card_embedding.reshape(1, -1))
        general_cc_pred = general_cc_model.predict(new_pair_embedding)
        general_pred = general_model.predict(card_embedding.reshape(1, -1))

        gen_cc_predicted_synergy_score = MLConverter().calc_synergy_score(general_cc_pred[0], individual_pred[0])
        gen_predicted_synergy_score = MLConverter().calc_synergy_score(general_pred[0], individual_pred[0])
        
        predicted_synergy_scores.append((commander_name, gen_predicted_synergy_score))
        analytics_data[card_name][commander_name] = round(gen_predicted_synergy_score, 2)
        print("GEN", commander_name, " ", round(gen_predicted_synergy_score, 2))

        cc_predicted_synergy_scores.append((commander_name, gen_cc_predicted_synergy_score))
        analytics_data[card_name]["".join([commander_name,"CC"])] = round(gen_cc_predicted_synergy_score, 2)
        print("GEN CC", commander_name, " ", round(gen_cc_predicted_synergy_score, 2))
    # In validation_set.json for each card:
        # "test_commanders": [
        #     "Gallia of the Endless Dance",
        #     "Grumgully, the Generous",
        #     "Jodah, Archmage Eternal",
        #     "Klothys, God of Destiny"
        # ],
        # "expected_high": [
        #     "Gallic of the Endless Dance",
        #     "Grumgully, the Generous"
        # ],
        # "expected_low": [
        #     "Jodah, Archmage Eternal",
        #     "Klothys, God of Destiny"
        # ],
        # "id": 999888,
        # "card_name": "Gronky the Gruul",
    # Create an accuracy score, "correct_list" and "incorrect_list"
    correct_list = []
    incorrect_list = []
    median_predicted_score = np.median([score for _, score in predicted_synergy_scores])
    for commander_name, predicted_score in predicted_synergy_scores:
        if commander_name in analytics_data[card_name]['expected_high']:
            if predicted_score >= median_predicted_score:
                correct_list.append((commander_name, predicted_score))
            else:
                incorrect_list.append((commander_name, predicted_score))
        elif commander_name in analytics_data[card_name]['expected_low']:
            if predicted_score < median_predicted_score:
                correct_list.append((commander_name, predicted_score))
            else:
                incorrect_list.append((commander_name, predicted_score))
        else:
            print("Commander not found in expected_high or expected_low", commander_name)
    
    alt_correct_list = []
    alt_incorrect_list = []
    median_predicted_score = np.median([score for _, score in cc_predicted_synergy_scores])
    for commander_name, predicted_score in cc_predicted_synergy_scores:
        temp_commander_name = commander_name[:-2]
        if temp_commander_name in analytics_data[card_name]['expected_high']:
            if predicted_score >= median_predicted_score:
                alt_correct_list.append((commander_name, predicted_score))
            else:
                alt_incorrect_list.append((commander_name, predicted_score))
        elif temp_commander_name in card['expected_low']:
            if predicted_score < median_predicted_score:
                alt_correct_list.append((commander_name, predicted_score))
            else:
                alt_incorrect_list.append((commander_name, predicted_score))
        else:
            print("Commander not found in expected_high or expected_low", commander_name)
            
    analytics_data[card_name]["accuracy"] = len(correct_list) / (len(correct_list) + len(incorrect_list))
    accuracy_scores.append(analytics_data[card_name]["accuracy"])
    analytics_data[card_name]["correct_list"] = correct_list
    analytics_data[card_name]["incorrect_list"] = incorrect_list

    analytics_data[card_name]["alt_accuracy"] = len(alt_correct_list) / (len(alt_correct_list) + len(alt_incorrect_list))
    alt_accuracy_scores.append(analytics_data[card_name]["alt_accuracy"])
    analytics_data[card_name]["alt_correct_list"] = alt_correct_list
    analytics_data[card_name]["alt_incorrect_list"] = alt_incorrect_list


analytics_data["average_accuracy"] = sum(accuracy_scores) / len(accuracy_scores)
print("Average accuracy:", analytics_data["average_accuracy"])
analytics_data["validation_data"] = validation_data

analytics_data["alt_average_accuracy"] = sum(alt_accuracy_scores) / len(alt_accuracy_scores)
print("Alt Average accuracy:", analytics_data["alt_average_accuracy"])
analytics_data["validation_data"] = validation_data

# use the datetime to create a unique file name, in analytics folder
if not os.path.exists("analytics"):
    os.makedirs("analytics")

now = datetime.datetime.now()
analytics_file_name = f"analytics/analytics_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"

with open(analytics_file_name, 'w') as file:
    json.dump(analytics_data, file, indent=4)
