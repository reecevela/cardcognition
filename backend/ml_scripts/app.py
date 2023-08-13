from card_embedder import CardEmbedder
from card_fetcher import CardsContext
import numpy as np
import pickle
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split

# Get all cards and commanders
context = CardsContext()
cards = context.get_all_cards()
commanders = context.get_commanders()

# Embed cards and commanders
embedder = CardEmbedder()
card_embeddings = embedder.embed_cards(cards)
commander_embeddings = embedder.embed_cards(commanders)

# Create and save mappings
card_id_to_index = {card['id']: index for index, card in enumerate(cards)}
commander_id_to_index = {commander['id']: index for index, commander in enumerate(commanders)}

with open('card_id_to_index.pkl', 'wb') as f:
    pickle.dump(card_id_to_index, f)
with open('commander_id_to_index.pkl', 'wb') as f:
    pickle.dump(commander_id_to_index, f)

# Save embeddings
np.save("card_embeddings.npy", card_embeddings)
np.save("commander_embeddings.npy", commander_embeddings)

# Construct examples
examples = []
for commander in commanders:
    commander_id = commander['id']
    commander_embedding = commander_embeddings[commander_id_to_index[commander_id]]
    synergies = context.get_commander_synergies_by_id(commander_id)
    for synergy in synergies:
        card_id = synergy['card_id']
        synergy_score = synergy['synergy_score']
        card_embedding = card_embeddings[card_id_to_index[card_id]]
        examples.append((commander_embedding, card_embedding, synergy_score))

# Combine embeddings and split data
X = [np.concatenate((commander_embedding, deck_card_embedding)) for commander_embedding, deck_card_embedding, _ in examples]
y = [score for _, _, score in examples]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train a Ridge regression model
model = Ridge(alpha=1.0)
model.fit(X_train, y_train)

# Evaluate the model
score = model.score(X_test, y_test)
print('Model R^2 Score:', score)

# Predict synergy score for a new pair, e.g. new_commander_embedding, new_deck_card_embedding
