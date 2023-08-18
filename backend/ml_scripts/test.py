from card_embedder import CardEmbedder
from card_fetcher import CardsContext
import json
import os
import datetime
import warnings
import time

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.linear_model import SGDRegressor
#from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
import numpy as np


with open('config.json', 'r') as f:
    config = json.load(f)
warnings.filterwarnings("ignore")

startTime = time.time()

db = CardsContext()

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
] # Solely because of Yargle, empty oracle text is allowed

card_name_map = {card['id']: card['card_name'] for card in cards_raw}
commander_name_map = {commander['card_id']: commander['card_name'] for commander in commanders_raw}

cards = {name: card for name, card in zip(card_name_map.values(), cards_raw)}
commanders = {name: cards[name] for name in commander_name_map.values()}

for i, card in enumerate(cards_raw):
    cards[card['card_name']] = card
    cards[card['card_name']]['index'] = i
    # This acts as a pointer to the card that
    # the rels can reference
    cards[card['id']] = card['card_name']

for i, commander in enumerate(commanders_raw):
    commanders[commander['card_name']] = cards[commander['card_name']]
    commanders[commander['card_name']]['index'] = i
    commanders[commander['card_name']]['cards'] = []
    # This acts as a pointer to the commander for rels
    commanders[commander['card_id']] = commander['card_name']

print(f"Cards: {len(cards)}")
print(f"Commanders: {len(commanders)}")
# Mapping rels to cards/commanders would be nice but a major performance bottleneck
# 500,000 rels, 30,000 cards, 1,900 commanders
# Note - rels are ordered by commander_id ASC
# cmd ordered by card_id ASC
# cards ordered by id ASC
# But rather than doing nested binary searches for each, we can just iterate once.

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

print(f"Relations: {len(rels)}")
print(f"Time Elapsed: {time.time() - startTime}")

embedder = CardEmbedder()
embeddings = embedder.embed_cards(cards_raw, testing=False)

for commander_name, commander_data in commanders.items():
    break
    try:
        # print(commander_name, " ", commander_data.get('id'))
        # print(len(commander_data.get('cards', [])))
        if commander_name not in commanders:
            # print(f"Skipping {commander_name} because it's not in the cards list")
            continue
        if len(commander_data.get('cards', 0)) < 100:
            # print(f"Skipping {commander_name} because it has {len(commander_data.get('cards', 0))} cards")
            continue
        X = []
        y = []
        for card in commander_data['cards']:
            # print(card[0]['card_name'], card[1])
            # print(embeddings[card[0].get('index')].shape)
            if card and card[0].get('index', None) is not None:
                X.append(embeddings[card[0]['index']])
                y.append(card[1] / 100)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        commanders[commander_name]['model'] = SGDRegressor(penalty=config["penalty"], alpha=config["alpha"])
        commanders[commander_name]['model'].fit(X_train, y_train)
        commanders[commander_name]['score'] = commanders[commander_name]['model'].score(X_test, y_test)

        # print(f"Score for {commander_name}: {commanders[commander_name]['score']}")
    except Exception as e:
        continue
        #print(f"Error for {commander_name}: {e}")

def generate_batches(batch_size, examples, concat=True):
    while True:
        examples = shuffle(examples)
        for i in range(0, len(examples), batch_size):
            if concat:
                batch_X = [np.concatenate((example[0], example[1])) for example in examples[i:i+batch_size]]
                batch_y = [example[2] for example in examples[i:i+batch_size]]
            else:
                batch_X = [example[0] for example in examples[i:i+batch_size]]
                batch_y = [example[1] for example in examples[i:i+batch_size]]

            yield np.array(batch_X), np.array(batch_y)

class CardBatchGenerator:
    def __init__(self, commanders):
        self.commanders = commanders
        self.commander_names = list(commanders.keys())
        self.index = 0
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.commander_names):
            self.index = 0
            raise StopIteration
        else:
            commander_name = self.commander_names[self.index]
            self.index += 1
            output = []
            for card in self.commanders[commander_name]['cards']:
                try:
                    output.append((np.concatenate(embeddings[self.commanders[commander_name]['index']], embeddings[card[0]['index']]), card[1]))
                except Exception as e:
                    continue
            return output

# Training a general model using all cards with CardBatchGenerator
batch_generator = CardBatchGenerator(commanders)
# Doesn't support partial fit, will try when I get a better laptop/PC
#gen_model = RandomForestRegressor(n_estimators=100, random_state=42) 
gen_model = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1, warm_start=True, random_state=42)

# Trained with (commander_embedding, card_embedding) -> frequency
X, y = [], []

for batch in batch_generator:
    batch_X, batch_y = generate_batches(config["batch_size"], [
        (commander_embedding, card_embedding, frequency) for commander_embedding, card_embedding, frequency in batch
    ], concat=True)
    gen_model.partial_fit(batch_X, batch_y, classes=[0])

# Validation Testing
with open("./validation_set.json", 'r') as file:
    validation_data = json.load(file)

analytics_data = dict()

for card in validation_data:
    card_embedding = embedder.embed_cards([card], testing=True)[0]
    card_predictions = dict()
    analytics_data[card['card_name']] = dict()

    for commander_name in card['test_commanders']:
        if commander_name not in commanders:
            # print(f"Skipping {commander_name} because it's not in the dataset")
            continue
        commander = commanders[commander_name]
        score = round(commander['model'].predict([card_embedding])[0], 4) * 100
        card_predictions[commander_name] = score

        # General model predicts commander + card frequency
        gen_score = round(gen_model.predict([[commander['index'], card['index']]])[0], 4) * 100
        analytics_data[card['card_name']]['general'] =[commander_name, gen_score]

    median = np.median(list(card_predictions.values()))
    correct_list = []
    incorrect_list = []
    for commander_name in card_predictions:
        if card_predictions[commander_name] >= median:
            if commander_name in card['expected_high']:
                correct_list.append((commander_name, card_predictions[commander_name]))
            else:
                incorrect_list.append((commander_name, card_predictions[commander_name]))
        else:
            if commander_name in card['expected_low']:
                correct_list.append((commander_name, card_predictions[commander_name]))
            else:
                incorrect_list.append((commander_name, card_predictions[commander_name]))
    accuracy = len(correct_list) / (len(correct_list) + len(incorrect_list))
    print(f"Accuracy for {card['card_name']}: {accuracy}")
    print(f"Correct: {correct_list}")
    print(f"Incorrect: {incorrect_list}")
    analytics_data[card['card_name']]['accuracy'] = accuracy
    analytics_data[card['card_name']]['correct'] = correct_list
    analytics_data[card['card_name']]['incorrect'] = incorrect_list

    gen_accuracy = 0
    total = 0
    for cmd_prediction in analytics_data[card['card_name']]['general']:
        if cmd_prediction[1] >= median:
            if commander_name in card['expected_high']:
                print(f"General Model Correct: {cmd_prediction}")
                gen_accuracy += 1
            else:
                print(f"General Model Incorrect: {cmd_prediction}")
        else:
            if commander_name in card['expected_low']:
                print(f"General Model Correct: {cmd_prediction}")
                gen_accuracy += 1
            else:
                print(f"General Model Incorrect: {cmd_prediction}")
        total += 1
    gen_accuracy /= total
    print(f"General Model Accuracy: {gen_accuracy}")


average_validation_accuracy = np.mean([analytics_data[card]['accuracy'] for card in analytics_data])
print(f"Average validation accuracy: {average_validation_accuracy}")
analytics_data['average_validation_accuracy'] = average_validation_accuracy

commander_sum_score = 0
count = 0
for commander_name, commander_data in commanders.items():
    try:
        commander_sum_score += commander_data.get('score', 0)
        count += 1
    except Exception as e:
        continue
average_commander_score = commander_sum_score / count
print(f"Average commander score: {average_commander_score}")
analytics_data['average_commander_score'] = average_commander_score

total_time_elapsed = time.time() - startTime
print(f"Total time elapsed: {total_time_elapsed}")
analytics_data['total_time_elapsed'] = total_time_elapsed

if not os.path.exists("analytics"):
    os.makedirs("analytics")

now = datetime.datetime.now()
analytics_file_name = f"analytics/analytics_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
analytics_data["config"] = config

with open(analytics_file_name, 'w') as file:
    json.dump(analytics_data, file, indent=4)
