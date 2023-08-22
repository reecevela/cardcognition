from converter import MLConverter
from card_fetcher import CardsContext
from card_embedder import CardEmbedder
import joblib
import os
import warnings
import json

warnings.filterwarnings("ignore")

converter = MLConverter()
context = CardsContext()
embedder = CardEmbedder()

with open('config.json', 'r') as f:
    config = json.load(f)

card_start = config['card_start']
card_stop = config['card_stop']
print_limit = config['print_limit']
min_count = config['min_count']

commander_names = [commander['card_name'] for commander in context.get_commanders() if os.path.exists(f"cmd_models/{converter.sanitize_filename(commander['card_name'])}.joblib")]
cards = context.get_all_cards()
cards = [
    card for card in cards
    if card['card_name'] is not None
    and card['type_line'] is not None
    and card['oracle_text'] is not None
    and '//' not in card['card_name'] 
    and '//' not in card['type_line'] 
][card_start:card_stop]

commander_scores = {commander_name: {card['card_name']: 0 for card in cards} for commander_name in commander_names}
scores = {card['card_name']: dict() for card in cards}

embeddings = embedder.embed_and_parse_cards(cards, testing=True)

# Collect raw scores
for i, card in enumerate(cards):
    try:
        if i % 100 == 0:
            print(f"Scoring {i} of {len(cards)}")
        card_embedding = embeddings[i]
        if card_embedding is None:
            continue
        for commander_name in commander_names:
            file_cmd_name = converter.sanitize_filename(commander_name)
            model = joblib.load(f"cmd_models/{file_cmd_name}.joblib")
            score = model.predict([card_embedding])[0]
            commander_scores[commander_name][card['card_name']] = score
            scores[card['card_name']][commander_name] = score
        if card['card_name'] == 'Urza, Lord High Artificer':
            print(scores[card['card_name']])
    except Exception as e:
        print(card['card_name'])
        print(len(scores[card['card_name']]))
        print(e)
        continue
with open('card_scores.txt', 'w') as f:
    for card_name, cmd_scores in scores.items():
        f.write(f"{card_name}\n")
        strings = [f"\t{commander}: {score}\n" for commander, score in sorted(cmd_scores.items(), key=lambda x: x[1])]
        strings = strings[:print_limit]
        f.write(''.join(strings))

with open('commander_scores.txt', 'w') as f:
    for commander_name, cmd_scores in commander_scores.items():
        f.write(f"{commander_name}\n")
        strings = [f"\t{card}: {score}\n" for card, score in sorted(cmd_scores.items(), key=lambda x: x[1]) if score > 0]
        strings = strings[:print_limit]
        f.write(''.join(strings))
