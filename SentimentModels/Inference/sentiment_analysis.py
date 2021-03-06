import os
from pathlib import Path

import json
import requests
import pickle as pk

class Sentiment_Analysis_TOAD:

    def __init__(self):
        full_path = Path(os.path.realpath(__file__))
        folderpath, _ = os.path.split(full_path)
        folderpath = Path(folderpath)
        self.shoppee_aspect_folderpath = folderpath.joinpath("Shopee_Aspect")

        filename = 'vectorizer_shopee_aspect.pk'
        filepath = self.shoppee_aspect_folderpath.joinpath(filename)
        self.vectorizer = pk.load(open(filepath, 'rb'))

        filename = 'logreg_model_shopee_aspect.sav'
        filepath = self.shoppee_aspect_folderpath.joinpath(filename)
        self.logres_loaded_model = pk.load(open(filepath, 'rb'))

        filename = 'SVM_model_shopee_aspect.sav'
        filepath = self.shoppee_aspect_folderpath.joinpath(filename)
        self.SVM_loaded_model = pk.load(open(filepath, 'rb'))

        self.spacy_URL_start_primary = 'https://danieltanhx2.pythonanywhere.com/?input='

    def logreg_model(self, TEST_REVIEW, negation_tag=False):
        test_vectors = self.vectorizer.transform([TEST_REVIEW])
        predME = self.logres_loaded_model.predict(test_vectors)
        pred = list(predME)

        if pred == [1.0]:
            if negation_tag:
                prediction = "Negative"
            else:
                prediction = "Positive"
        else:
            if negation_tag:
                prediction = "Positive"
            else:
                prediction = "Negative"

        return prediction


    def SVM_model(self, TEST_REVIEW, negation_tag=False):
        test_vectors = self.vectorizer.transform([TEST_REVIEW])
        predME = self.SVM_loaded_model.predict(test_vectors)
        pred = list(predME)
        
        if pred == [1.0]:
            if negation_tag:
                prediction = "Negative"
            else:
                prediction = "Positive"
        else:
            if negation_tag:
                prediction = "Positive"
            else:
                prediction = "Negative"

        return prediction

    def spacy_model(self, TEST_REVIEW, negation_tag=False):
        url_primary = self.spacy_URL_start_primary + str(TEST_REVIEW)
        
        r = requests.get(url_primary)
        pred = json.loads(r.text)["Predicted sentiment"]
        
        if negation_tag:
            if pred == 'Positive':
                prediction = 'Negative'
            elif pred == 'Negative':
                prediction = 'Positive'
        else:
            prediction = pred
        
        return prediction


if __name__ == "__main__":

    SA_TOAD = Sentiment_Analysis_TOAD()

    print("Logistic Regression Model")
    print("This shirt is good")
    print(SA_TOAD.logreg_model("This shirt is good", False))
    print("This shirt is bad")
    print(SA_TOAD.logreg_model("This shirt is bad", False))
    print("This shirt is not bad")
    print(SA_TOAD.logreg_model("This shirt is not bad", False))
    print("This shirt is good (with negation_tag)")
    print(SA_TOAD.logreg_model("This shirt is good", True))
    print("")

    print("Support Vector Machine")
    print("This shirt is good")
    print(SA_TOAD.SVM_model("This shirt is good", False))
    print("This shirt is bad")
    print(SA_TOAD.SVM_model("This shirt is bad", False))
    print("This shirt is not bad")
    print(SA_TOAD.SVM_model("This shirt is not bad", False))
    print("This shirt is good (with negation_tag)")
    print(SA_TOAD.SVM_model("This shirt is good", True))
    print("")

    print("Finetuned Spacy Model")
    print("This shirt is good")
    print(SA_TOAD.spacy_model("This shirt is good", False))
    print("This shirt is bad")
    print(SA_TOAD.spacy_model("This shirt is bad", False))
    print("This shirt is not bad")
    print(SA_TOAD.spacy_model("This shirt is not bad", False))
    print("This shirt is good (with negation_tag)")
    print(SA_TOAD.spacy_model("This shirt is good", True))
    print("")