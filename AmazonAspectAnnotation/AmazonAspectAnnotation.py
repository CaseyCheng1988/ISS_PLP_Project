import pandas as pd
import json, random, os

maindataFile = 'Dataset/AMAZON_FASHION.json'
metadataFile = 'Dataset/meta_AMAZON_FASHION.json'
annotateddataFile = 'Dataset/AMAZON_FASHION_annotated.json'

def readData(filename):
    data = []
    with open(filename) as json_file:
        for line in json_file:
            data.append(json.loads(line))

    # for i in range(10): print(data[i])

    return data

def dataValidate(prompt, valid_list, error_text):
    while(True):
        term = input(prompt)
        if term not in valid_list:
            print(f'Term not found in {error_text}. Please try again...')
            continue
        break
    return term

data = readData(maindataFile)
metadata = readData(metadataFile)

if not os.path.exists(annotateddataFile):
    with open(annotateddataFile, 'w'): pass

data_annotated = readData(annotateddataFile)
review_annotated = [review['reviewText'] for review in data_annotated]
numReviewAnnotated = len(data_annotated)
print(f'Total Annotated Data: {numReviewAnnotated}')

while(True):
    index = random.randint(0, len(data)-1)
    review = data[index]
    print(index)
    print(review)
    try:
        if review['reviewText'] in review_annotated: continue
    except:
        continue

    print('\n')
    print(review['reviewText'])

    aspectList = []
    while(True):
        aspectTerm = input('Aspect Term: ')
        if aspectTerm == 'next' or aspectTerm == 'exit':
            break
        elif aspectTerm not in review['reviewText']:
            print('Aspect term not found in review text. Please try again...')
            continue

        aspectSentTerm = dataValidate('Aspect Sentiment Term: ', review['reviewText'], 'review')
        aspectSent = dataValidate('Aspect Sentiment: ', ['+', '-', '='], '(+, -, =)')
        aspectList.append({'aspectTerm': aspectTerm, 'aspectSentTerm': aspectSentTerm, 'aspectSent': aspectSent})
        print('\n')

    if aspectTerm == 'exit': break

    review['aspect'] = aspectList
    with open(annotateddataFile, 'a') as f:
        if numReviewAnnotated > 0: f.write('\n')
        json.dump(review, f)
    numReviewAnnotated += 1
