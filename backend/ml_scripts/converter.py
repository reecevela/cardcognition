from gensim.models.phrases import Phrases

class MLConverter:
    def __init__(self, data_source):
        # Would like to use Dependency injection here
        # Maybe to be able to use in-memory for testing and postgres for production
        self.data_source = data_source

    def encode_colors(self, colors:str) -> list:
        # Converts MtG color to binary representation
        # [W, U, B, R, G] - 1 if color is present, 0 otherwise
        # Input ex: "WBU"
        output = [0, 0, 0, 0, 0]
        colors = ["W", "U", "B", "R", "G"]
        for i, color in enumerate(colors):
            if color in colors:
                output[i] = 1
        return output
    
    def phrase_oracle_text(self, oracle_texts:list, threshold:int = 3) -> list:
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
        tokenized_oracle_texts = [oracle_text.split(" ") for oracle_text in oracle_texts]
        phrase_model = Phrases(tokenized_oracle_texts, min_count=threshold, threshold=threshold)
        return [phrase_model[oracle_text] for oracle_text in tokenized_oracle_texts]