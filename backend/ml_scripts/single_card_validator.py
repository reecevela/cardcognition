from converter import MLConverter
from card_fetcher import CardsContext
from card_embedder import CardEmbedder
import joblib
import os
import warnings

warnings.filterwarnings("ignore")

converter = MLConverter()
context = CardsContext()
embedder = CardEmbedder()

commander_names = [commander['card_name'] for commander in context.get_commanders() if os.path.exists(f"cmd_models/{converter.sanitize_filename(commander['card_name'])}.joblib")]
cards = context.get_all_cards()
cards = [
    card for card in cards[:100]
    if card['card_name'] is not None
    and card['type_line'] is not None
    and card['oracle_text'] is not None
    and '//' not in card['card_name'] 
    and '//' not in card['type_line'] 
]
# Initialize max and min score for each commander
commander_score_bounds = {commander_name: {'min': float('inf'), 'max': float('-inf')} for commander_name in commander_names}
raw_scores = {card['card_name']: {} for card in cards}

embeddings = embedder.embed_cards(cards, testing=True)

# Collect raw scores and update max and min for each commander
for i, card in enumerate(cards):
    try:
        if i % 100 == 0:
            print(f"Scoring {i} of {len(cards)}")
        card_embedding = embeddings[i]
        if card_embedding is None:
            continue
        for commander_name in commander_names:
            if os.path.exists(f"cmd_models/{commander_name}.joblib"):
                file_cmd_name = converter.sanitize_filename(commander_name)
                model = joblib.load(f"cmd_models/{file_cmd_name}.joblib")
                score = model.predict([card_embedding])[0]
                raw_scores[card['card_name']][commander_name] = score
                commander_score_bounds[commander_name]['min'] = min(commander_score_bounds[commander_name]['min'], score)
                commander_score_bounds[commander_name]['max'] = max(commander_score_bounds[commander_name]['max'], score)
    except Exception as e:
        continue

# Normalize the scores
scores = {card['card_name']: [] for card in cards}
for card_name, card_scores in raw_scores.items():
    for commander_name, raw_score in card_scores.items():
        min_score = commander_score_bounds[commander_name]['min']
        max_score = commander_score_bounds[commander_name]['max']
        normalized_score = (raw_score - min_score) / (max_score - min_score) if max_score != min_score else 0
        scores[card_name].append((commander_name, normalized_score))

with open('card_results.txt', 'w') as f:
    for card_name, score_list in scores.items():
        f.write(f"{card_name}\n")
        score_list.sort(key=lambda x: x[1], reverse=True)
        for score in score_list[:100]:
            f.write(f"\t'{score[0]}', --{score[1]}\n")
        f.write("\n")
