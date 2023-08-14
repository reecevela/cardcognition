from tensorflow_hub import KerasLayer
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MultiLabelBinarizer
from converter import MLConverter
from card_fetcher import CardsContext
import time
import json

class CardEmbedder:
    def __init__(self):
        self.text_embedder = KerasLayer("https://tfhub.dev/google/universal-sentence-encoder/4")
        self.converter = MLConverter()
        self.context = CardsContext()

        card_types, sub_types = self.context.get_all_card_types_and_sub_types()

        validation_set = None
        with open("validation_set.json", "r") as f:
            validation_set = json.load(f)

        val_card_types, val_sub = self.context.get_card_types_and_sub_types(validation_set)
        card_types.extend(val_card_types)
        sub_types.extend(val_sub)
        
        self.card_type_encoder = OneHotEncoder()
        self.card_type_encoder.fit(np.array(card_types).reshape(-1, 1))
        
        self.sub_types_encoder = MultiLabelBinarizer()
        self.sub_types_encoder.fit(sub_types)
        self.default_embedding_shape = self.text_embedder(["Legendary Creature — Elf Warrior"]).shape

        with open("config.json", "r") as f:
            config = json.load(f)
        
        self.min_count = config["min_count"]
        self.threshold = config["threshold"]
        self.npmi_scoring = config["npmi_scoring"]

    def embed_cards(self, cards:list) -> np.ndarray:
        oracle_texts = [card.get("oracle_text", "") for card in cards]

        # Review oracle_texts.txt to see outputs for different min_count, threshold and npmi values
        phrased_oracle_texts = self.converter.phrase_oracle_text(oracle_texts, min_count=3, threshold=0.5, npmi_scoring=False)
        phrased_oracle_texts_str = [" ".join(phrased_text) for phrased_text in phrased_oracle_texts]

        start_time = time.time()
        total_cards = len(cards)

        embeddings = []
        FINAL_EMBEDDING_SHAPE = None
        for i, card in enumerate(cards):
            try:
                colors = np.array(self.converter.encode_colors(card.get("colors"))).reshape(1, -1)

                phrased_oracle_text = phrased_oracle_texts_str[i]
                if phrased_oracle_text == "":
                    oracle_text_embedding = np.zeros(self.default_embedding_shape)
                else:
                    oracle_text_embedding = self.text_embedder([phrased_oracle_text]).numpy()

                cmc = np.array([card["cmc"]]).reshape(1, -1)
                
                card_type, sub_types = self.converter.process_type_line(card["type_line"])

                # power = card.get("power")
                # if power is None or np.isnan(power):
                #     power = 0
                # power = np.array([power]).reshape(1, -1)

                # toughness = card.get("toughness")
                # if toughness is None or np.isnan(toughness):
                #     toughness = 0
                # toughness = np.array([toughness]).reshape(1, -1)

                card_type_embedding = self.card_type_encoder.transform([[card_type]]).toarray() 
                sub_types_embedding = self.sub_types_encoder.transform(sub_types).sum(axis=0, keepdims=True)

                # Removed power and toughness from here
                final_embedding = np.concatenate((colors, oracle_text_embedding, cmc, card_type_embedding, sub_types_embedding), axis=1).reshape(-1)
                if FINAL_EMBEDDING_SHAPE is None:
                    FINAL_EMBEDDING_SHAPE = final_embedding.shape
                embeddings.append(final_embedding)
            except Exception as e:
                try:
                    print("Lost " + card["card_name"])
                    print(e)
                    default_embedding = np.zeros(FINAL_EMBEDDING_SHAPE)
                    embeddings.append(default_embedding)
                except:
                    print(e)
                    print(card)

            if i % 100 == 0:
                elapsed_time = time.time() - start_time
                progress = (i+1) / total_cards
                remaining_time = elapsed_time * (1-progress) / progress
                print(f"Progress: {progress*100:.2f}%, Time remaining: {remaining_time:.2f}s Loss Percent: {(len(embeddings) - i)/(i+0.001)*100:.2f}% Time elapsed: {elapsed_time:.2f}s")

        return np.array(embeddings)
