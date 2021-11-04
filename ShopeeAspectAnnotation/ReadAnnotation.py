import pickle

annotateddataFile = 'Shopee_annotated.pkl'

def readData(filename):
    with open(filename, 'rb') as f:
        try:
            data = pickle.load(f)
        except:
            data = []
    return data

data = readData(annotateddataFile)
for review in data: print(review)
