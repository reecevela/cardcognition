from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDRegressor
import json

from card_embedder import CardEmbedder
from card_fetcher import CardsContext

### CONFIGURATION ###

features = {
    "exclude_colors": True,
    "exclude_oracle_text": True,
    "exclude_power": True,
    "exclude_toughness": True,
    "exclude_cmc": False,
    "exclude_super_types": True,
    "exclude_type_line": False,
    "exclude_sub_types": True,
    "clean_text": True,
    "oracle_text_encoding_method": "TFIDF"
}

embedder = CardEmbedder(features)
db = CardsContext()

# Copied from test.py
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

embeddings = embedder.embed_cards(cards_raw, testing=False)

with open('config.json', 'r') as f:
    config = json.load(f)

### DATA TRANSFORMATION ###
# Goal here: We'll look at how cards cluster in a Jhoira, Weatherlight Captain deck

commander = commanders['Jhoira, Weatherlight Captain']
commander_index = commander['index']

cmd_specific_cards = [card[0]['index'] for card in commander['cards']]

cmd_specific_cards.append(commander['index'])

print(len(cmd_specific_cards), "cards in Jhoira, Weatherlight Captain deck.")

cmd_card_embeddings = [embeddings[card_id] for card_id in cmd_specific_cards]

features = np.array(cmd_card_embeddings).reshape(len(cmd_card_embeddings), -1)
### DATA VISUALIZATION ###

# Standardize the features
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features) # features is your dataset

# Reduce dimensions to 2
pca = PCA(n_components=2)
reduced_features = pca.fit_transform(features_scaled)

# Apply K-Means clustering
kmeans = KMeans(n_clusters=5) # You can choose a different number of clusters
clusters = kmeans.fit_predict(reduced_features)

# Plot the 2D visualization
plt.scatter(reduced_features[:, 0], reduced_features[:, 1], c=clusters, cmap='viridis')
plt.xlabel('CMC')
plt.ylabel('Typeline')
plt.title('Clustering of Card Features')
plt.colorbar().set_label('Cluster')
plt.show()
