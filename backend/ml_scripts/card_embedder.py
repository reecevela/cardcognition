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
        
        for key in config:
            if key == "oracle_text_encoding_method":
                self.oracle_text_encoding_method = config[key]
            elif key == "vector_size":
                self.vector_size = config[key]
            elif key == "window":
                self.window = config[key]
            elif key == "min_count":
                self.min_count = config[key]
            elif key == "threshold":
                self.threshold = config[key]
            elif key == "npmi_scoring":
                self.npmi_scoring = config[key]
            elif key == "clean_text":
                self.clean_text = config[key]
            elif key == "freq_cutoff":
                self.freq_cutoff = config[key]

    def embed_cards(self, cards:list) -> np.ndarray:
        oracle_texts = [card.get("oracle_text", "") for card in cards]

        start_time = time.time()
        total_cards = len(cards)

        if self.oracle_text_encoding_method == "USE":
            oracle_text_embeddings = self.converter.embed_USE_oracle_texts(oracle_texts, clean_text=self.clean_text)
        elif self.oracle_text_encoding_method == "TFIDF":
            oracle_text_embeddings = self.converter.embed_tfidf_oracle_texts(oracle_texts, freq_cutoff=self.freq_cutoff)
        elif self.oracle_text_encoding_method == "W2V":
            oracle_text_embeddings = self.converter.embed_oracle_texts(oracle_texts, vector_size=self.vector_size, window=self.window, clean_text=self.clean_text)
        elif self.oracle_text_encoding_method == "PHR":
            oracle_text_embeddings = self.converter.embed_phrased_oracle_texts(oracle_texts, min_count=self.min_count, threshold=self.threshold, npmi_scoring=self.npmi_scoring, clean_text=self.clean_text, window=self.window, vector_size=self.vector_size)
        
        
        embeddings = []
        FINAL_EMBEDDING_SHAPE = None
        for i, card in enumerate(cards):
            try:
                colors = np.array(self.converter.encode_colors(card.get("colors"))).reshape(1, -1)

                oracle_text_embedding = np.array(oracle_text_embeddings[i]).reshape(1, -1)

                power = card.get("power")
                power = np.array(self.converter.encode_power_or_toughness(power)).reshape(1, -1)

                toughness = card.get("toughness")
                toughness = np.array(self.converter.encode_power_or_toughness(toughness)).reshape(1, -1)

                cmc = np.array([card["cmc"]]).reshape(1, -1)
                
                card_type, sub_types = self.converter.process_type_line(card["type_line"])

                card_type_embedding = self.card_type_encoder.transform([[card_type]]).toarray() 
                sub_types_embedding = self.sub_types_encoder.transform(sub_types).sum(axis=0, keepdims=True)


                final_embedding = np.concatenate((colors, oracle_text_embedding, power, toughness, cmc, card_type_embedding, sub_types_embedding), axis=1).reshape(-1)
                if FINAL_EMBEDDING_SHAPE is None:
                    FINAL_EMBEDDING_SHAPE = final_embedding.shape
                embeddings.append(final_embedding)
            except Exception as e:
                try:
                    print("Lost " + card["card_name"])
                    # print(e)
                    default_embedding = np.zeros(FINAL_EMBEDDING_SHAPE)
                    embeddings.append(default_embedding)
                except:
                    print(e)
                    print(card)

            if i % 1000 == 0:
                elapsed_time = time.time() - start_time
                progress = (i+1) / total_cards
                remaining_time = elapsed_time * (1-progress) / progress
                print(f"Progress: {progress*100:.2f}%, Time remaining: {remaining_time:.2f}s Loss Percent: {(len(embeddings) - i)/(i+0.001)*100:.2f}% Time elapsed: {elapsed_time:.2f}s")

        return np.array(embeddings)

    def test_embedding_methods(self, cards:list):
        oracle_texts = [card.get("oracle_text", "") for card in cards]
        
        embeddings = []
        oracle_text_embeddings = self.converter.embed_USE_oracle_texts(oracle_texts, clean_text=self.clean_text)
        print(oracle_text_embeddings[0])
        print(oracle_text_embeddings.shape)
        for i, card in enumerate(cards):
            oracle_text_embedding = np.array(oracle_text_embeddings[i]).reshape(1, -1)
            embeddings.append(oracle_text_embedding)
        print(np.array(embeddings).shape)

        embeddings = []
        oracle_text_embeddings = self.converter.embed_oracle_texts(oracle_texts, vector_size=self.vector_size, window=self.window, clean_text=self.clean_text)
        print(oracle_text_embeddings[0])
        print(oracle_text_embeddings.shape)
        for i, card in enumerate(cards):
            oracle_text_embedding = np.array(oracle_text_embeddings[i]).reshape(1, -1)
            embeddings.append(oracle_text_embedding)
        print(np.array(embeddings).shape)

        embeddings = []
        oracle_text_embeddings = self.converter.embed_phrased_oracle_texts(oracle_texts, min_count=self.min_count, threshold=self.threshold, npmi_scoring=self.npmi_scoring, clean_text=self.clean_text)
        print(oracle_text_embeddings[0])
        print(oracle_text_embeddings.shape)
        for i, card in enumerate(cards):
            oracle_text_embedding = np.array(oracle_text_embeddings[i]).reshape(1, -1)
            embeddings.append(oracle_text_embedding)
        print(np.array(embeddings).shape)
        