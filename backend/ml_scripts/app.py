from card_embedder import CardEmbedder
from card_fetcher import CardsContext
import numpy as np
import pickle
import json
import pandas as pd
from sklearn.linear_model import Ridge, SGDRegressor
from sklearn.model_selection import train_test_split
import time
from sklearn.utils import shuffle
from sklearn.impute import SimpleImputer

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
i = 0
j = 0
for commander_card_id in commander_id_to_index:
    # Commander's scryfall_cards id
    commander_id = context.get_cmd_id_from_sc_id(commander_card_id)
    # embedding for the actual card itself
    commander_embedding = card_embeddings[card_id_to_index[commander_card_id]]

    synergies = context.get_commander_synergies_by_id(commander_id)
    for synergy in synergies:
        i += 1
        card_id = synergy['card_id']
        synergy_score = synergy['synergy_score']
        try:
            card_embedding = card_embeddings[card_id_to_index[card_id]]
        except Exception as e:
            continue
        examples.append((commander_embedding, card_embedding, synergy_score))
    j += 1
    if j % 100 == 0:
        elapsed_time = time.time() - start_time
        progress = (j+1) / total_commanders
        remaining_time = elapsed_time * (1-progress) / progress
        print(f"Progress: {progress*100:.2f}%, Time remaining: {remaining_time:.2f}s Loss Percent: {(len(examples) - i)/(i+0.001)*100:.2f}% Loss Count: {len(examples) - i} Time elapsed: {elapsed_time:.2f}s")

print("Starting training...")


# Have to do this otherwise the amount of memory crashes my laptop
def generate_batches(batch_size, examples, imputer):
    while True:
        examples = shuffle(examples)
        for i in range(0, len(examples), batch_size):
            batch_X = [example[0] for example in examples[i:i+batch_size]]
            batch_y = [example[2] for example in examples[i:i+batch_size]]

            yield np.array(batch_X), np.array(batch_y)

print("Splitting data...")
# Combine enbeddings and split data (without storing X and y in memory)
train_examples, test_examples = train_test_split(examples, test_size=0.2, train_size=0.6)

print("Fitting the imputer...")
imputer = SimpleImputer(strategy='constant', fill_value=0)
imputer.fit([example[0] for example in train_examples[:1000]])

batch_size = 10000
print("Generating training batches...")
train_batches = generate_batches(batch_size, train_examples, imputer=imputer)
print("Generating testing batches...")
test_batches = generate_batches(batch_size, test_examples, imputer=imputer)

model = SGDRegressor(penalty='l2', alpha=1.0)

# Train the model using partial_fit
for i in range(0, len(train_examples), batch_size):
    print("Training batch", i, "of", len(train_examples))
    batch_X, batch_y = next(train_batches)
    model.partial_fit(batch_X, batch_y)

# Evaluate the model
X_test, y_test = next(test_batches) # Assuming test_examples size is at least batch_size
score = model.score(X_test, y_test)
print('Model R^2 Score:', score)

# Validate some fake/custom cards

# Load validation set
with open("./validation_set.json", 'r') as file:
    validation_data = json.load(file)

# Create a DataFrame to store the results
results_df = pd.DataFrame(columns=['Card_Name', 'Commander', 'Predicted_Synergy_Score'])

# Iterate through validation data
for record in validation_data:
    card_name = record['card_name']

    embedder = CardEmbedder()
    card_embedding = embedder.embed_cards([record])

    print("Validating card:", card_name)
    # Iterate through the test_commanders
    for commander_name in record['test_commanders']:
        print("Validating commander:", commander_name)
        commander_id = context.get_id_by_name(commander_name)[0].id
        print("Commander ID:", commander_id)
        commander_embedding = card_embeddings[card_id_to_index[commander_id]]

        # Combine embeddings and predict synergy score
        new_pair_embedding = np.concatenate((commander_embedding, card_embedding))
        predicted_synergy_score = model.predict([new_pair_embedding])
        print("Predicted Synergy Score:", predicted_synergy_score[0])
        # Append to DataFrame
        results_df = results_df.append({
            'Card_Name': card_name,
            'Commander': commander_name,
            'Predicted_Synergy_Score': predicted_synergy_score[0]
        }, ignore_index=True)

# Save the DataFrame to a CSV file
results_df.to_csv('validation_results.csv', index=False)
