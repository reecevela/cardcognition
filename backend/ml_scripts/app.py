from card_embedder import CardEmbedder
from card_fetcher import CardsContext
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

# Load config.json
with open("config.json", "r") as f:
    config = json.load(f)

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

start_time = time.time()
total_commanders = len(commanders)
# Construct examples
examples = []
print("Mapping synergies...")

lock = Lock()

def process_chunk(start, end, id:int):
    i = 0
    j = 0
    card_errors = 0
    cmd_errors = 0
    local_examples = []
    for commander in commanders[start:end]:
        # print(commander['card_name'])
        # Commander's scryfall_cards id
        try:
            commander_card_id = commander['id']
            commander_id = context.get_cmd_id_from_sc_id(commander_card_id)
            commander_embedding = card_embeddings[card_id_to_index[commander_card_id]]
            synergies = context.get_commander_synergies_by_id(commander_id)
        except Exception as e:
            # print(f"Error getting commander id from scryfall id: {commander_card_id}")
            cmd_errors += 1
            continue
            
        for card in synergies:
            i += 1
            try:
                card_id = card['card_id']
                synergy_score = card['synergy_score']
            except Exception as e:
                # print(f"Error processing card: {card}")
                card_errors += 1
                continue
            try:
                card_embedding = card_embeddings[card_id_to_index[card_id]]
            except Exception as e:
                # Can ignore, generally caused by dual-faced cards
                # print(f"Error getting card embedding from card id: {card_id}")
                card_errors += 1
                continue
            local_examples.append((commander_embedding, card_embedding, synergy_score))
        j += 1
        if j % 10 == 0:
            elapsed_time = time.time() - start_time
            progress = (j+1) / (end - start)
            remaining_time = elapsed_time * (1-progress) / progress
            print(f"Progress: {progress*100:.2f}%, Time remaining: {remaining_time:.2f}s Time elapsed: {elapsed_time:.2f}s CMD Errors: {cmd_errors} Card Errors: {card_errors} ID: {id}")

        with lock:
            examples.extend(local_examples)

chunk_size = len(commanders) // config['num_threads']
threads = []

for i in range(config['num_threads']):
    start = i * chunk_size
    end = (i + 1) * chunk_size if i != config['num_threads'] - 1 else len(commanders)
    threads.append(threading.Thread(target=process_chunk, args=(start, end, i)))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print("Starting training...")

# Have to do this otherwise the amount of memory crashes my laptop
def generate_batches(batch_size, examples):
    while True:
        examples = shuffle(examples)
        for i in range(0, len(examples), batch_size):
            batch_X = [np.concatenate((example[0], example[1])) for example in examples[i:i+batch_size]]
            batch_y = [example[2] for example in examples[i:i+batch_size]]

            yield np.array(batch_X), np.array(batch_y)

print("Splitting data...")
# Combine enbeddings and split data (without storing X and y in memory)
train_examples, test_examples = train_test_split(examples, test_size=0.2, train_size=0.8)


batch_size = config['batch_size']
print("Generating training batches...")
train_batches = generate_batches(batch_size, train_examples)
print("Generating testing batches...")
test_batches = generate_batches(batch_size, test_examples)

model = SGDRegressor(penalty=config["penalty"], alpha=config["alpha"])

# Train the model using partial_fit
for i in range(0, len(train_examples), batch_size):
    print("Training batch", i, "of", len(train_examples))
    batch_X, batch_y = next(train_batches)
    model.partial_fit(batch_X, batch_y)

# Evaluate the model
X_test, y_test = next(test_batches)
score = model.score(X_test, y_test)
print('Model R^2 Score:', score)

# Validate some fake/custom cards

with open("./validation_set.json", 'r') as file:
    validation_data = json.load(file)

analytics_data = {"score": score}
analytics_data["config"] = config
accuracy_scores = []

converter = CardEmbedder()
# Iterate through validation data
for card in validation_data:
    card_name = card['card_name']
    card_embedding = converter.embed_cards([card]).reshape(-1)
    print(card_name)
    analytics_data[card_name] = {}
    predicted_synergy_scores = []

    for commander_name in card['test_commanders']:
        commander_id = context.get_id_by_name(commander_name)[0]['id']
        commander_embedding = np.array(card_embeddings[card_id_to_index[commander_id]]).reshape(-1,)

        # Combine embeddings and predict synergy score
        new_pair_embedding = np.concatenate((commander_embedding, card_embedding)).reshape(1, -1)

        predicted_synergy_score = model.predict(new_pair_embedding)
        predicted_synergy_scores.append((commander_name, predicted_synergy_score[0]))
        analytics_data[card_name][commander_name] = round(predicted_synergy_score[0], 2)
        print(commander_name, " ", round(predicted_synergy_score[0], 2))
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
        if commander_name in card['expected_high']:
            if predicted_score >= median_predicted_score:
                correct_list.append((commander_name, predicted_score))
            else:
                incorrect_list.append((commander_name, predicted_score))
        elif commander_name in card['expected_low']:
            if predicted_score < median_predicted_score:
                correct_list.append((commander_name, predicted_score))
            else:
                incorrect_list.append((commander_name, predicted_score))
        else:
            print("Commander not found in expected_high or expected_low", commander_name)
            
    analytics_data[card_name]["accuracy"] = len(correct_list) / (len(correct_list) + len(incorrect_list))
    accuracy_scores.append(analytics_data[card_name]["accuracy"])
    analytics_data[card_name]["correct_list"] = correct_list
    analytics_data[card_name]["incorrect_list"] = incorrect_list

analytics_data["average_accuracy"] = sum(accuracy_scores) / len(accuracy_scores)
analytics_data["validation_data"] = validation_data

# use the datetime to create a unique file name, in analytics folder
if not os.path.exists("analytics"):
    os.makedirs("analytics")

now = datetime.datetime.now()
analytics_file_name = f"analytics/analytics_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"

with open(analytics_file_name, 'w') as file:
    json.dump(analytics_data, file, indent=4)
