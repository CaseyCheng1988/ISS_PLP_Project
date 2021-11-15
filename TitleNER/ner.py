import spacy
from config import PROJ_DIR, NER_MODEL


ner_model = spacy.load(NER_MODEL)

def get_entities(text, nlp_model=ner_model):
    doc = nlp_model(text)
    output = {'BRAND':[], 'MODEL':[], 'TYPE':[], 'VAR_SIZE':[], 'VAR_COLOUR':[],'VAR_QTY':[],'DEMOGRAPHIC':[]}
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

if __name__ == "__main__":
    entities = get_entities('Fjallraven Kanken Classic Backpack - Red Series', ner_model)
    print(entities)