from gensim.models.phrases import Phrases
import re

class MLConverter:
    def process_type_line(self, type_line: str):
        if type_line is None:
            return None, []

        if ' — ' not in type_line:
            return type_line, []

        card_type, sub_types_str = type_line.split(' — ', 1)
        sub_types_list = sub_types_str.split(' ')

        return card_type, sub_types_list

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
    
    def phrase_oracle_text(self, oracle_texts:list, min_count:int = 1, threshold:int = 1, npmi_scoring:bool = False) -> list:
        # Tokenizes oracle text, then phrases it to group words that are often together
        # Input ex: [
        #   "Whenever CARDNAME enters the battlefield or attacks, ...",
        #   "CARDNAME gets +1/+1 until end of turn.", 
        #   "When CARDNAME enters the battlefield, ..."
        # ]
        # Output ex: [
        #   ["Whenever", "CARDNAME", "enters_the_battlefield", "or", "attacks", ...],
        #   ["CARDNAME", "gets", "+1/+1", "until_end_of_turn"],
        #   ["When", "CARDNAME", "enters_the_battlefield", ...]
        # ]
        tokenized_oracle_texts = []
        for oracle_text in oracle_texts:
            if oracle_text is None or oracle_text == "":
                tokenized_oracle_texts.append("")
                continue
            # Replace all numbers greater than 1 with NUM to prevent them from being grouped
            # But leaving 1 because of +1/+1 counters, -1/-1 counters, etc.
            oracle_text = re.sub(r"\b[2-9]\b", "NUM", oracle_text)
            # Replace periods with spaces to prevent them from being grouped
            oracle_text = oracle_text.replace(".", " ")
            oracle_text = oracle_text.replace(",", "")
            tokenized_oracle_text = oracle_text.lower().replace("\n", " ").split(" ")
            tokenized_oracle_texts.append(tokenized_oracle_text)

        if npmi_scoring:
            phrase_model = Phrases(tokenized_oracle_texts, min_count=min_count, threshold=threshold, scoring='npmi')
        else:
            phrase_model = Phrases(tokenized_oracle_texts, min_count=min_count, threshold=threshold)           
        return [phrase_model[oracle_text] for oracle_text in tokenized_oracle_texts]
    
    def test_several_phrase_values(self, oracle_texts:list) -> dict:
        output = {}
        # Nested in several layers, taking the same card example for tons of permutations/nested layers

        for min_count in range(1, 11, 2):
            print(round(((min_count-1) / 10) * 100, 2))
            for threshold in [-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1]:
                output[f"{min_count}_{threshold}_npmi"] = self.phrase_oracle_text(oracle_texts, min_count=min_count, threshold=threshold, npmi_scoring=True)[:3]
            for threshold in [0.3, 0.5, 0.8, 1, 1.5, 1.8, 2, 3, 4, 5, 10, 20]:
                output[f"{min_count}_{threshold}"] = self.phrase_oracle_text(oracle_texts, min_count=min_count, threshold=threshold)[:3]
        
        return output
            