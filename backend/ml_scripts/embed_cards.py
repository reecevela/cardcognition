import pickle
import numpy as np
from card_embedder import CardEmbedder
from card_fetcher import CardsContext

# Get all cards and commanders
context = CardsContext()
cards = context.get_all_cards()
commanders = context.get_commanders()

# Filter out split cards
cards = [card for card in cards if '//' not in card['card_name']]
commanders = [commander for commander in commanders if '//' not in commander['card_name']]

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