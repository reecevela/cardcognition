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
with open('validation_set.json', 'r') as f:
    cards = json.load(f)

testing_commanders = []
for card in cards:
    testing_commanders.extend(card['test_commanders'])
commander_names = [commander_name for commander_name in commander_names if commander_name in testing_commanders]

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
            score = round(model.predict([card_embedding])[0], 2)
            commander_scores[commander_name][card['card_name']] = score
            scores[card['card_name']][commander_name] = score
    except Exception as e:
        print(card['card_name'])
        print(len(scores[card['card_name']]))
        print(e)
        continue

with open('validation_scores.txt', 'w') as f:
    for card_name, cmd_scores in scores.items():
        f.write(f"{card_name}\n")
        strings = [f"\t{commander}: {score}\n" for commander, score in sorted(cmd_scores.items(), key=lambda x: x[1], reverse=True)]
        strings = strings[:print_limit]
        f.write(''.join(strings))

    for commander_name, cmd_scores in commander_scores.items():
        f.write(f"{commander_name}\n")
        strings = [f"\t{card}: {score}\n" for card, score in sorted(cmd_scores.items(), key=lambda x: x[1], reverse=True) if score > 0]
        strings = strings[:print_limit]
        f.write(''.join(strings))

from card_fetcher import CardsContext
import numpy as np
context = CardsContext()

commanders = context.get_commanders()
commanders = [commander for commander in commanders if commander['card_name'] in commander_names]
commander_embeddings = embedder.embed_and_parse_cards(commanders, testing=True)

commander_name_embedding_pairs = [(commander['card_name'], commander_embedding) for commander, commander_embedding in zip(commanders, commander_embeddings) if commander_embedding is not None]

# Open the gen model
gen_model = joblib.load('gen_model.sav')


for commander_name, commander_embedding in commander_name_embedding_pairs:
    for card_name, card_embedding in zip([card['card_name'] for card in cards], embeddings):
        if card_embedding is None:
            continue
        combined_input = np.concatenate((commander_embedding, card_embedding)).reshape(1, -1)
        gen_score = round(gen_model.predict(combined_input)[0], 2)
        scores[card_name][commander_name] = gen_score
        commander_scores[commander_name][card_name] = gen_score

with open('validation_gen_scores.txt', 'w') as f:
    for card_name, cmd_scores in scores.items():
        f.write(f"{card_name}\n")
        strings = [f"\t{commander}: {score}\n" for commander, score in sorted(cmd_scores.items(), key=lambda x: x[1], reverse=True)]
        strings = strings[:print_limit]
        f.write(''.join(strings))

    for commander_name, cmd_scores in commander_scores.items():
        f.write(f"{commander_name}\n")
        strings = [f"\t{card}: {score}\n" for card, score in sorted(cmd_scores.items(), key=lambda x: x[1], reverse=True) if score > 0]
        strings = strings[:print_limit]
        f.write(''.join(strings))



