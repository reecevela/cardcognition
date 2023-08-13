from card_embedder import CardEmbedder
from card_fetcher import CardsContext
import numpy as np

# commanders: CardsContext.get_commanders()
# cards: CardsContext.get_all_cards()
cards = CardsContext().get_all_cards()
embedder = CardEmbedder()

embeddings = embedder.embed_cards(cards)

# card_embeddings.npy
# commanders_embeddings.npy
np.save("card_embeddings.npy", embeddings)
