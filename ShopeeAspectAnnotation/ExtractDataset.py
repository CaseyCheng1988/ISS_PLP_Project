import pickle

filename = 'reviews.pkl'
extractdataFile = 'reviews_extract.pkl'

with open(filename, 'rb') as f:
    data = pickle.load(f)

start = int(input('Start #: '))
numDataset = int(input('# of Datapoints: '))

extractData = data[start:start+numDataset]

with open(extractdataFile, 'wb') as f:
    pickle.dump(extractData, f)
