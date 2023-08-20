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
average_scores = {commander_name: 0 for commander_name in commander_names}
count_scores = {commander_name: 0 for commander_name in commander_names}

print(commander_names[:10])

cards = context.get_all_cards()
cards = [
    card for card in cards
    if card['card_name'] is not None
    and card['type_line'] is not None
    and card['oracle_text'] is not None
    and '//' not in card['card_name'] 
    and '//' not in card['type_line'] 
]
scores = {card['card_name']: [] for card in cards}
embeddings = embedder.embed_cards(cards, testing=True)

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
                score = model.predict([card_embedding])
                average_scores[commander_name] += score
                count_scores[commander_name] += 1
                scores[card['card_name']].append((commander_name, score))
    except Exception as e:
        continue

for commander_name in commander_names:
    if count_scores[commander_name] > 0:
        average_scores[commander_name] /= count_scores[commander_name]

# Normalize the scores for each card's commander, since some commanders produce higher scores for any given card
for card in cards:
    for i, score in enumerate(scores[card['card_name']]):
        scores[card['card_name']][i] = (score[0], score[1] - average_scores[score[0]])
    scores[card['card_name']].sort(key=lambda x: x[1], reverse=True)
    print(f"{card['card_name']}: {[scores[card['card_name']][i][0] for i in range(10)]}")

#'card_resulsts.txt'
with open('card_results.txt', 'w') as f:
    for card_name, score_list in scores.items():
        f.write(f"{card_name}\n")
        for score in score_list[:100]:
            f.write(f"\t'{score[0]}', --{score[1]}\n")
        f.write("\n")