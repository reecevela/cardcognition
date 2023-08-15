from gensim.models.phrases import Phrases
from gensim.models import Word2Vec
from tensorflow_hub import KerasLayer
import re
import numpy as np

class MLConverter:
    def __init__(self):
        self.text_embedder = KerasLayer("https://tfhub.dev/google/universal-sentence-encoder/4")

    def calc_synergy_score(self, inclusion_rate, base_rate):
        return (inclusion_rate / base_rate if base_rate != 0 else inclusion_rate)

    def process_type_line(self, type_line: str):
        if type_line is None:
            return None, []

        if ' — ' not in type_line:
            return type_line, []

        card_type, sub_types_str = type_line.split(' — ', 1)
        sub_types_list = sub_types_str.split(' ')

        return card_type, sub_types_list
    
    def encode_power_or_toughness(self, value: str)-> list:
        # Categories:
        # 0: No power/NULL
        # 1: Special/*
        # 2: power >= 0
        # 3: power >= 1
        # ...
        # 8: power >= 8
        encodings = [0 for _ in range(9)]
        if value is None or value == "":
            encodings[0] = 1
            return encodings
        try:
            value = int(value)
        except:
            encodings[1] = 1
            return encodings
        for i in range(2, 9):
            if value >= i-2:
                encodings[i] = 1
        return encodings


    def encode_colors(self, card_colors:str) -> list:
        # Converts MtG color to binary representation
        # [W, U, B, R, G] - 1 if color is present, 0 subwise
        # Input ex: "WBU"
        output = [0, 0, 0, 0, 0]
        colors = ["W", "U", "B", "R", "G"]
        for i, color in enumerate(colors):
            if color in card_colors:
                output[i] = 1
        return output
    
    def embed_USE_oracle_texts(self, oracle_texts:list, clean_text:bool=False) -> list:
        oracle_texts = [text if text else "" for text in oracle_texts]
        if clean_text:
            oracle_texts = self._clean_texts(oracle_texts)
        # Embed the texts using the Universal Sentence Encoder
        embeddings = self.text_embedder(oracle_texts)
        return embeddings
    
    def embed_oracle_texts(self, oracle_texts:list, vector_size:int=100, window:int=5, clean_text:bool=False) -> list:
        if clean_text:
            oracle_texts = self._clean_texts(oracle_texts)
        sentences = [text.lower().split() if text else [] for text in oracle_texts]

        model = Word2Vec(sentences, vector_size=vector_size, window=window, min_count=1, workers=4)

        embeddings = []
        for text in sentences:
            if text:
                embeddings.append(model.wv[text])
            else:
                embeddings.append(np.zeros((1, model.vector_size)))
        return embeddings

    def embed_phrased_oracle_texts(self, oracle_texts:list, min_count:int = 1, threshold:int = 1, npmi_scoring:bool = False, clean_text:bool=False) -> list:
        tokenized_oracle_texts = []
        if clean_text:
            oracle_texts = self._clean_texts(oracle_texts)
        for oracle_text in oracle_texts:
            tokenized_oracle_texts.append(oracle_text.split())

        if npmi_scoring:
            phrase_model = Phrases(tokenized_oracle_texts, min_count=min_count, threshold=threshold, scoring='npmi')
        else:
            phrase_model = Phrases(tokenized_oracle_texts, min_count=min_count, threshold=threshold)           
        embeddings = []
        for oracle_text in tokenized_oracle_texts:
            embeddings.append(phrase_model[oracle_text])
        return embeddings
            
    def _clean_texts(self, oracle_texts:list) -> list:
        output_texts = []
        for oracle_text in oracle_texts:
            if oracle_text is None or oracle_text == "":
                output_texts.append("")
                continue
            # Replace all numbers greater than 1 with NUM to prevent them from being grouped
            # But leaving 1 because of +1/+1 counters, -1/-1 counters, etc.
            oracle_text = re.sub(r"\b[2-9]\b", "NUM", oracle_text)
            # Replace periods with spaces to prevent them from being grouped
            oracle_text = oracle_text.replace(".", " ")
            oracle_text = oracle_text.replace(",", "").lower().replace("\n", " ")
            output_texts.append(oracle_text)
        return output_texts