from card_embedder import CardEmbedder
from card_fetcher import CardsContext
import numpy as np
import pickle
import json
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
import time

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
    if j % 10 == 0:
        elapsed_time = time.time() - start_time
        progress = (j+1) / total_commanders
        remaining_time = elapsed_time * (1-progress) / progress
        print(f"Progress: {progress*100:.2f}%, Time remaining: {remaining_time:.2f}s Loss Percent: {(len(examples) - i)/(i+0.001)*100:.2f}% Loss Count: {len(examples) - i} Time elapsed: {elapsed_time:.2f}s")

print("Starting training...")

# Combine embeddings and split data
X = [np.concatenate((commander_embedding, deck_card_embedding)) for commander_embedding, deck_card_embedding, _ in examples]
y = [score for _, _, score in examples]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, train_size=0.6)

# Train a Ridge regression model
model = Ridge(alpha=1.0)
model.fit(X_train, y_train)

# Evaluate the model
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
    card_id = context.get_id_by_name(card_name)
    card_embedding = card_embeddings[card_id_to_index[card_id]]

    # Iterate through the test_commanders
    for commander_name in record['test_commanders']:
        commander_id = context.get_id_by_name(commander_name)
        commander_embedding = card_embeddings[card_id_to_index[commander_id]]

        # Combine embeddings and predict synergy score
        new_pair_embedding = np.concatenate((commander_embedding, card_embedding))
        predicted_synergy_score = model.predict([new_pair_embedding])

        # Append to DataFrame
        results_df = results_df.append({
            'Card_Name': card_name,
            'Commander': commander_name,
            'Predicted_Synergy_Score': predicted_synergy_score[0]
        }, ignore_index=True)

# Save the DataFrame to a CSV file
results_df.to_csv('validation_results.csv', index=False)
