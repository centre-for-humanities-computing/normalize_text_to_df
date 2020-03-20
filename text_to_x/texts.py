"""

"""

# Imports ...
from text_to_x.text_to_df import TextToDf
from text_to_x.text_to_sentiment import TextToSentiment
import warnings


class Texts():
    def __init__(self, texts, 
                 language = None,  
                 detect_lang_fun = "polyglot", 
                 **kwargs):
        """
        texts (list): texts to process.
        language (str): language code(s), if None language is detected using detect_lang_fun (which defaults to polyglot). Can be list of codes.
        detect_lang_fun (str|fun): fucntion to use for language detection. default is polyglot. But you can specify a user function, which return         
        """

        self.raw_texts = texts
        self.__kwargs = kwargs
        self.language = language
        self.__preprocess_method = None
        self.preprocessors = None
        self.__detect_lang_fun = detect_lang_fun
        self.__sentiment_scores = None
        
        if self.language is None:
            self.language = self.__detect_languages(detect_lang_fun)

        self.__preprocessed_texts = None
        self.is_preprocessed = False
        
    def __detect_languages(self, detect_lang_fun):
        if isinstance(detect_lang_fun, str):
            if detect_lang_fun == "polyglot":
                from text_to_x.utils import detect_lang_polyglot
                detect_lang_fun = detect_lang_polyglot
            else:
                # detect_lang_fun_dict = {"polyglot": detect_lang_polyglot}
                # detect_lang_fun = detect_lang_fun_dict[detect_lang_fun]
                raise ValueError("'polyglot' is currently the only accepted string value of detect_lang_fun.")
        elif not callable(detect_lang_fun):
            raise TypeError(f"detect_lang_fun should be a string or callable not a {type(detect_lang_fun)}")
        return [detect_lang_fun(text, **self.__kwargs) for text in self.raw_texts]

    def __check_preprocessed(self, method_name, required_processes = None):
        assert required_processes is None or isinstance(required_processes, (str, list)), \
            "required_processes must be a list of strings or None."
        if not self.is_preprocessed:
            raise RuntimeError(f"{method_name} requires the preprocessing() method to be run first.")
        if required_processes is not None and not set(required_processes).issubset(set(self.preprocessors)):
            raise RuntimeError(f"{method_name} requires these preprocessing steps: {required_processes}")

    def preprocess(self, 
                   preprocess_method = "stanfordnlp", 
                   preprocessors = ["tokenize", "mwt", "lemma", "pos", "depparse"]):
        """
        preprocess_method (str|fun): method used for normalization
        preprocessors (list): names of processes to apply in the preprocessing stage

        Note: Overwrites previous preprocessing!
        """

        if self.is_preprocessed:
            warnings.warn("Overwriting previous preprocessing.")

        self.__preprocess_method = preprocess_method
        self.preprocessors = preprocessors
        self.__preprocessor_args = {"processor": ",".join(self.preprocessors)}

        self.__preprocessed_ttd = TextToDf(lang = self.language, 
                       method = self.__preprocess_method, 
                       args = self.__preprocessor_args)
        self.__preprocessed_texts = self.__preprocessed_ttd.texts_to_dfs(texts = self.raw_texts)
        self.is_preprocessed = True

    def get_preprocessed_texts(self):
        if self.__preprocessed_texts is None:
            raise RuntimeError("The preprocess() method has not been called yet.")
        return self.__preprocessed_texts

    def score_sentiment(self, method = "dictionary", type_token = None):
        """
        method ("dictionary"|"bert"|fun): method used for sentiment analysis
        type_token (None|'lemma'|'token'): The type of token used. If None is chosen to be token automatically depending on method.
          'lemma' for dictionary otherwise 'token'.

        Requires these preprocessing steps: 
          "tokenize", "lemma"

        Use get_sentiments() method to extract scores.
        """
        self.__check_preprocessed("score_sentiment()", ["tokenize","lemma"])
        tts = TextToSentiment(lang=self.language, method=method, type_token=type_token)
        self.__sentiment_scores = tts.texts_to_sentiment(self.__preprocessed_ttd)

    def get_sentiments(self):
        if self.__sentiment_scores is None:
            raise RuntimeError("The score_sentiment() method has not been called yet.")
        return self.__sentiment_scores

    def model_topics(self):
        # self.__check_preprocessed("model_topics()", ["tokenize","lemma"])
        pass

    def get_topics(self):
        pass



# testing code
if __name__ == "__main__":
    #import os
    #os.getcwd()
    #os.chdir("..")
    # make some data
    with open("test_data/fyrtårnet.txt", "r") as f:
        text = f.read()
        # just some splits som that the text aren't huge
    t1 = "\n".join([t for t in text.split("\n")[1:50] if t])
    t2 = "\n".join([t for t in text.split("\n")[50:100] if t])
    t3 = "\n".join([t for t in text.split("\n")[100:150] if t])

    # we will test it using a list but a single text will work as well
    texts = [t1, t2, t3]

    # Init Texts object
    tt = Texts(texts, languages = "da")
    tt.preprocess()
    print(tt.get_preprocessed_texts())
    # Score sentiment
    tt.score_sentiment()
    print(tt.get_sentiments())
    # Topic modeling
    # tt.model_topics()


    


    