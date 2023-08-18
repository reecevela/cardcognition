from converter import MLConverter
from card_fetcher import CardsContext
from gensim import corpora, models

converter = MLConverter()
db = CardsContext()

cards = db.get_all_cards()
oracle_texts = [card.get("oracle_text", "") for card in cards]

tokens_list = []

temp_frequency = {}
for oracle_text in oracle_texts:
    tokens = converter.remove_common_words_to_list(oracle_text)
    tokens_list.append(tokens)
    for token in tokens:
        temp_frequency[token] = temp_frequency.get(token, 0) + 1
    

tokens_list = [[word for word in token if temp_frequency[word] > 1] for token in tokens_list]

dictionary = corpora.Dictionary(tokens_list)
dictionary.filter_tokens(bad_ids=[tokenid for tokenid, docfreq in dictionary.dfs.items() if docfreq < 5])
dictionary.compactify()
corpora.Dictionary.save(dictionary, "gensim_dictionary.dict")

corpus = [dictionary.doc2bow(token) for token in tokens_list]
corpora.MmCorpus.serialize("gensim_corpus.mm", corpus)

tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]
corpora.MmCorpus.serialize("gensim_corpus_tfidf.mm", corpus_tfidf)
