from gensim.models.phrases import Phrases
from gensim.models import Word2Vec
from gensim import corpora, models
from tensorflow_hub import KerasLayer
import re
import numpy as np
import json

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
    
    def embed_tfidf_oracle_texts(self, oracle_texts:list, freq_cutoff:int=5) -> list:
        tokens_list = []

        temp_frequency = {}
        for oracle_text in oracle_texts:
            tokens = self.remove_common_words_to_list(oracle_text)
            tokens_list.append(tokens)
            for token in tokens:
                temp_frequency[token] = temp_frequency.get(token, 0) + 1
            
        tokens_list = [[word for word in token if temp_frequency[word] > 1] for token in tokens_list]

        dictionary = corpora.Dictionary(tokens_list)
        dictionary.filter_tokens(bad_ids=[tokenid for tokenid, docfreq in dictionary.dfs.items() if docfreq < freq_cutoff])
        dictionary.compactify()
        corpora.Dictionary.save(dictionary, "gensim_dictionary.dict")

        corpus = [dictionary.doc2bow(token) for token in tokens_list]
        corpora.MmCorpus.serialize("gensim_corpus.mm", corpus)

        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        corpora.MmCorpus.serialize("gensim_corpus_tfidf.mm", corpus_tfidf)

        return corpus_tfidf

    
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

    def embed_phrased_oracle_texts(self, oracle_texts:list, vector_size:int, min_count:int = 1, threshold:int = 1, npmi_scoring:bool = False, clean_text:bool=False, window:int=5) -> np.array:
        tokenized_oracle_texts = []
        if clean_text:
            oracle_texts = self._clean_texts(oracle_texts)
        for oracle_text in oracle_texts:
            tokenized_oracle_texts.append(oracle_text.split())

        if npmi_scoring:
            phrase_model = Phrases(tokenized_oracle_texts, min_count=min_count, threshold=threshold, scoring='npmi')
        else:
            phrase_model = Phrases(tokenized_oracle_texts, min_count=min_count, threshold=threshold)
        
        phrased_texts = [phrase_model[oracle_text] for oracle_text in tokenized_oracle_texts]
        
        word2vec_model = Word2Vec(phrased_texts, vector_size=vector_size, window=window)
        
        embeddings = []
        for text in phrased_texts:
            vectors = [word2vec_model.wv[word] for word in text if word in word2vec_model.wv]
            if vectors:
                embeddings.append(np.mean(vectors, axis=0))
            else:
                embeddings.append(np.zeros(vector_size))

        return np.array(embeddings)

            
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
    
    def remove_common_words_to_list(self, sentence:str) -> list:
        with open("oracle_rm_list.json", "r") as f:
            rm_json = json.load(f)

        if not sentence:
            return []
        sentence = sentence.lower()

        sentence = sentence.replace("{", " ").replace("}", " ")
        
        for char in rm_json["rm_chars"]:
            sentence = sentence.replace(char, "")
        
        for original in rm_json["replacements"].keys():
            replacement = rm_json["replacements"][original]
            sentence = sentence.replace(original, replacement)
        
        # Deal with costs by splitting them up
        # 3{4}{u}{u} => 3 4 u u

        sentence = sentence.split()

        output = []
        for word in sentence:
            if word[:4] == 'non-':
                word = word[4:]
            if word[:-2] == 'es' or word[:-2] == 'ed':
                word = word[:-2]        
            if word in rm_json["rm_words"]:
                continue
            # if word in output:
            #     continue
            if word[:-1] == 's' and len(word) > 2 and word[len(word) - 3] not in ['a', 'e', 'i', 'o', 'u']:
                word = word[:-1]
            output.append(word)

        return output
