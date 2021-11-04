# 1. Size
# 2. Comfort
# 3. Appearance
# 4. Quality
# 5. Functionality
# 6. Price
# 7. Delivery
# 8. General (?)

import pandas as pd
import json, os, pickle, sys

maindataFile = 'reviews.pkl'
annotateddataFile = 'Shopee_annotated.pkl'
aspectCatList = ['Size', 'Comfort', 'Appearance', 'Quality', 'Functionality', 'Price', 'Delivery', 'Anecdotes/Misc']

def readData(filename):
    with open(filename, 'rb') as f:
        try:
            data = pickle.load(f)
        except:
            data = []

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

if not os.path.exists(annotateddataFile):
    with open(annotateddataFile, 'wb'): pass

print(f'Total Data: {len(data)}')

index = int(input('Start Index: '))

while(True):

    data_annotated = readData(annotateddataFile)
    numReviewAnnotated = len(data_annotated)
    if numReviewAnnotated != 0:
        review_annotated = [review['reviewText'] for review in data_annotated]
    else:
        review_annotated = []
    print(f'Total Annotated Data: {numReviewAnnotated}')

    if len(data) == numReviewAnnotated:
        print('All data annotated... Exiting')
        sys.exit()

    review = data[index]

    if review in review_annotated:
        index+=1
        continue

    print('\n')

    print(index)
    annotatedReview = {}
    annotatedReview['index'] = index
    annotatedReview['reviewText'] = review

    aspectList = []
    while(True):
        print(review)
        print('Identify existing aspect categories based on list below: ')
        for cat in aspectCatList:
            print('    ' + cat)
        aspectCat = input('Aspect Category: ')
        if aspectCat == 'next' or aspectCat == 'exit':
            break
        elif aspectCat not in aspectCatList:
            print('Aspect category not found in category list. Please try again...')
            continue

        aspectTerm = dataValidate('Aspect Term: ', annotatedReview['reviewText'], 'review')
        aspectSentTerm = dataValidate('Aspect Sentiment Term: ', annotatedReview['reviewText'], 'review')
        aspectSent = dataValidate('Aspect Sentiment: ', ['+', '-', '=', '~'], '(+, -, =, ~)')
        aspectList.append({'aspectCat': aspectCat, 'aspectTerm': aspectTerm, 'aspectSentTerm': aspectSentTerm, 'aspectSent': aspectSent})
        print('\n')

    if aspectCat == 'exit': break

    annotatedReview['aspect'] = aspectList
    # print(annotatedReview)
    # print(data_annotated)
    data_annotated.append(annotatedReview)

    with open(annotateddataFile, 'wb') as f:
        pickle.dump(data_annotated, f)

    index += 1
