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

        #     def process_type_line(self, type_line: str)-> dict:
        # supertypes = ["Basic", "Legendary", "Ongoing", "Snow", "World"]
        # types = ["Artifact", "Creature", "Enchantment", "Instant", "Land", "Planeswalker", "Sorcery", "Tribal"]
        # separator = "—"

        # super_types = []
        # card_types = []
        # sub_types = []

        # # "Legendary Artifact Creature —  Elder Golem Warrior" might be an example
        # if separator not in type_line:
        #     for s in supertypes:
        #         if s in type_line:
        #             super_types.append(s)
        #             type_line = type_line.replace(s, "")
        #     for t in types:
        #         if t in type_line:
        #             card_types.append(t)
        #             type_line = type_line.replace(t, "")
        # sub_types = type_line.split().remove(separator)
        # return {"super_types": super_types, "card_types": card_types, "sub_types": sub_types}
        #
        # Needs to implement the above and be refactored

        super_types, card_types, sub_types = self.context.get_all_card_types_and_sub_types()

        validation_set = None
        with open("validation_set.json", "r") as f:
            validation_set = json.load(f)

        val_super_types, val_card_types, val_sub = self.context.get_card_types_and_sub_types(validation_set)
        super_types.extend(val_super_types)
        card_types.extend(val_card_types)
        sub_types.extend(val_sub)

        self.super_type_encoder = MultiLabelBinarizer()
        self.super_type_encoder.fit(super_types)

        
        self.card_type_encoder = MultiLabelBinarizer()
        self.card_type_encoder.fit(card_types)
        
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

    def embed_cards(self, cards:list, testing=False) -> np.ndarray:
        oracle_texts = [card.get("oracle_text", "") for card in cards]

        start_time = time.time()
        total_cards = len(cards)

        if self.oracle_text_encoding_method == "USE":
            oracle_text_embeddings = self.converter.embed_USE_oracle_texts(oracle_texts, clean_text=self.clean_text)
        elif self.oracle_text_encoding_method == "TFIDF":
            oracle_text_embeddings = self.converter.embed_tfidf_oracle_texts(oracle_texts, freq_cutoff=self.freq_cutoff, testing=testing)
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

                power = card.get("power", "")
                power = np.array(self.converter.encode_power_or_toughness(power)).reshape(1, -1)

                toughness = card.get("toughness", "")
                toughness = np.array(self.converter.encode_power_or_toughness(toughness)).reshape(1, -1)

                cmc = np.array([card["cmc"]]).reshape(1, -1)
                
                super_types, card_types, sub_types = self.converter.process_type_line(card["type_line"])

                super_type_embedding = self.super_type_encoder.transform(super_types).sum(axis=0, keepdims=True)
                card_type_embedding = self.card_type_encoder.transform(card_types).sum(axis=0, keepdims=True)
                sub_types_embedding = self.sub_types_encoder.transform(sub_types).sum(axis=0, keepdims=True)


                final_embedding = np.concatenate(
                    (
                        #colors, 
                        oracle_text_embedding, 
                        #power, 
                        #toughness, 
                        #cmc, 
                        #super_type_embedding,
                        card_type_embedding, 
                        sub_types_embedding
                    ), axis=1).reshape(-1)
                if FINAL_EMBEDDING_SHAPE is None:
                    FINAL_EMBEDDING_SHAPE = final_embedding.shape
                    print(colors.shape, oracle_text_embedding.shape, power.shape, toughness.shape, cmc.shape, super_type_embedding.shape, card_type_embedding.shape, sub_types_embedding.shape, final_embedding.shape)
                embeddings.append(final_embedding)
            except Exception as e:
                try:
                    print("Lost " + card["card_name"])
                    with open("errors.txt", "a") as f:
                        f.write(card + "\n")
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
        print("Shape: ", np.array(embeddings).shape, " Cards embedded: ", len(embeddings))
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
        oracle_text_embeddings = self.converter.embed_tfidf_oracle_texts(oracle_texts, freq_cutoff=self.freq_cutoff)
        print(oracle_text_embeddings[0])
        print(oracle_text_embeddings.shape)
        for i, card in enumerate(cards):
            oracle_text_embedding = np.array(oracle_text_embeddings[i]).reshape(1, -1)
            embeddings.append(oracle_text_embedding)
        print(np.array(embeddings).shape)
        