import spacy
import os
import sys

mod_dir = os.path.dirname(__file__)
main_dir = os.path.dirname(mod_dir)
sys.path.append(main_dir)

from SentimentModels.Inference.sentiment_analysis import Sentiment_Analysis_TOAD
from collections import Counter

def load_ab_model(path = os.path.join(mod_dir, 'ner_model')):
    return spacy.load(path)

def load_sa_model(path = os.path.join(mod_dir, 'textcat_model')):
    return spacy.load(path)

def get_aspects(text, nlp_model):
    doc = nlp_model(text)
    output = {'SIZE':[], 'COMFORT':[], 'APPEARANCE':[], 'QUALITY':[], 'PRICE':[],'DELIVERY':[]}
    buffer = []
    buffer_type = ''
    for idx, token in enumerate(doc):
        if token.ent_iob_ == 'B':
            if len(buffer) != 0:
                output[buffer_type].append(' '.join(buffer))
                buffer = []
            buffer.append(str(token))
            buffer_type = token.ent_type_

        elif token.ent_iob_ == 'O':
            continue

        else:
            buffer.append(str(token))

    if len(buffer) != 0:
        output[buffer_type].append(' '.join(buffer))

    return output

def aspects2sentiments(entities, model):
    res = {}
    for aspects in entities.keys():
        res[aspects] = []
        for aspect in entities[aspects]:
            cats = model(aspect).cats
            res[aspects].append(max(cats, key=cats.get))

    for aspect in res.keys():
        if len(res[aspect]) == 0:
            res[aspect] = None
        else:
            c = Counter(res[aspect])
            res[aspect] = c.most_common()[0][0]
    return res

if __name__ == "__main__":
    ab_mod = load_ab_model()
    sa_mod = load_sa_model()

    eg_text = 'Good quality of jeans. Fast delivery. Definitely will order again.'

    aspects = get_aspects(eg_text, ab_mod)
    sents = aspects2sentiments(aspects, sa_mod)
