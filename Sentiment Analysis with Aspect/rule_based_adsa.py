import pandas as pd
import csv
import numpy as np

import spacy
from spacy import displacy

import os
from pathlib import Path
import sys

full_path = Path(os.path.realpath(__file__))
folderpath, _ = os.path.split(full_path)
folderpath = Path(folderpath)
model_folderpath = folderpath.parent.joinpath("SentimentModels").joinpath("Inference")
sys.path.insert(1, str(model_folderpath))
from SentimentModels.Inference.sentiment_analysis import Sentiment_Analysis_TOAD

class Rule_Based_ADSA:

	def __init__(self):

		self.SA_TOAD = Sentiment_Analysis_TOAD()

		full_path = Path(os.path.realpath(__file__))
		folderpath, _ = os.path.split(full_path)
		self.folderpath = Path(folderpath)
		self.wordnet_folderpath = self.folderpath.parent.joinpath("WordNet")

		self.nlp = spacy.load("en_core_web_sm")
		self.topic_list = ['size', 'comfort', 'appearance', 'quality', 'price', 'delivery']
		self.noun_keywords = self.update_noun_keywords()
		self.adjective_keywords = self.update_adjective_keywords()


	def update_noun_keywords(self):
		noun_keywords = { 'size'          : ['size', 'fit', 'length'],
						  'comfort'       : [],
						  'appearance'    : ['colour', 'picture', 'design', 'style', 'photo'],
						  'quality'       : ['quality', 'material', 'fabric', 'leather'],
						  'price'         : ['price', 'money'],
						  'delivery'      : ['time', 'day', 'seller', 'shipping', 'order']}
					 
		for topic in self.topic_list:
			filename = topic + '.csv'
			filepath = self.wordnet_folderpath.joinpath(topic).joinpath(filename)
			
			with open(filepath, newline='\n') as f:
				reader = csv.reader(f)
				data = list(reader)
			nouns = noun_keywords[topic] + [pair[0] for pair in data if pair[1] == 'noun']
			noun_keywords[topic] = list(dict.fromkeys(nouns))
		
		return noun_keywords


	def update_adjective_keywords(self):
		adjective_keywords = { 'size'          : ['small', 'large', 'little', 'big', 'fit', 'long', 'short', 'tight', 'loose', 'medium', 'tiny', 'huge'],
							   'comfort'       : ['comfortable', 'uncomfortable', 'soft', 'lightweight','comfy'],
							   'appearance'    : ['beautiful', 'stylish', 'flattering', 'gorgeoous', 'lovely', 'sexy', 'adorable', 'cool'],
							   'quality'       : ['durable', 'sturdy', 'heavy', 'thick', 'new', 'old', 'hard'],
							   'price'         : ['cheap', 'expensive', 'honest', 'worth'],
							   'delivery'      : ['fast', 'quick']}

		for topic in self.topic_list:
			filename = topic + '.csv'
			filepath = self.wordnet_folderpath.joinpath(topic).joinpath(filename)
			
			with open(filepath, newline='\n') as f:
				reader = csv.reader(f)
				data = list(reader)
			adjectives = adjective_keywords[topic] + [pair[0] for pair in data if pair[1] == 'adj']
			adjective_keywords[topic] = list(dict.fromkeys(adjectives))
		
		return adjective_keywords	


	def find_noun_head(self, token):
		#print(f"Finding Token: {token}")
		#print(f"Token Head: {token.head}")
		if token.head.pos_ == "NOUN" or token.head.pos_ == "NOUN" or token.head.dep_ == "ROOT":
			#print("Found")
			return token.head
		else:
			#print("Continue Search")
			return self.find_noun_head(token.head)
	

	def find_negation_tag(self, adjective):
		#print(f"Finding Negatation for Adjective: {adjective}")
		#print(f"Token Head: {adjective.head}")
		if adjective.head.dep_ == "neg":
			return True
		elif adjective.head.pos_ == "AUX":
			for child in adjective.head.children:
				if child.dep_ =='neg':
					return True
		return False


	def find_span_start(self, sent, token):
		#for tok in sent:
		#    print(f"{tok.i}: {tok} - {tok.pos_}")
		#print(f"Start {token.i}: {token} - {token.pos_}")  
		if token.i == sent.start or sent[token.i-1].pos_ == "PUNCT":
			#print(token.i)
			return token.i
		else:
			#print(token.i-1)
			return self.find_span_start(sent, sent[token.i-1])

	def find_span_end(self, sent, token):
		#for tok in sent:
		#    print(f"{tok.i}: {tok} - {tok.pos_}")
		#print(f"End {token.i}: {token} - {token.pos_}")        
		if token.i+1 == sent.end or sent[token.i+1].pos_ == "PUNCT":
			#print(token.i+1)
			return token.i+1
		else:
			#print(token.i+1)
			return self.find_span_end(sent, sent[token.i+1])
	

	def match_topics(self, noun_token, adjective_token, topic_list, noun_keywords, adjective_keywords):

		for topic in self.topic_list:
			if noun_token.lemma_ in noun_keywords[topic]:
				return topic
			elif adjective_token.lemma_ in adjective_keywords[topic]:
				return topic

		return None


	def rule_based_ADSA_model(self, review, DEBUG = False, SENTI_MODEL = 'logreg'):

		#Model Setting
		SENTI_MODEL = SENTI_MODEL
		DEBUG = DEBUG

		#Model    
		doc = self.nlp(review)

		topic_prediction = {'size'          : None,
							'comfort'       : None,
							'appearance'    : None,
							'quality'       : None,
							'price'         : None, 
							'delivery'      : None}

		topic_positive = {'size'          : 0.0,
						'comfort'     	  : 0.0,
						'appearance'  	  : 0.0,
						'quality'     	  : 0.0,
						'price'       	  : 0.0, 
						'delivery'    	  : 0.0}
	
		topic_total = {'size'             : 0.0,
						'comfort'     	  : 0.0,
						'appearance'  	  : 0.0,
						'quality'     	  : 0.0,
						'price'       	  : 0.0, 
						'delivery'    	  : 0.0}

		sent_count = 0
		descriptor_pair = []
		for sent in doc.sents:
			sent_count += 1

			adjectives = [tok for tok in sent if tok.pos_ == "ADJ"]
			pronouns = [tok for tok in sent if tok.pos_ == "PRON"]
			nouns = [tok for tok in sent if tok.pos_ == "NOUN"]
			negations = [tok for tok in sent if tok.dep_ == "neg"]
			
			if DEBUG:
				print(f"Sentence {sent_count}: {sent}")
				img = displacy.render(sent, style="dep", jupyter = False)
				output_path = self.folderpath.joinpath("displacy_img.svg")
				output_path.open("w", encoding="utf-8").write(img)
				print(f"Adjectives: {adjectives}")
				print(f"Nouns: {nouns}")
				print(f"Pronouns: {pronouns}")
				print(f"Negations: {negations}")
				print("")

			for adjective in adjectives:
				isFound = False
				topic = None
				
				try:
					descriptor = ""
					for child in adjective.children:
						if child.pos_ == "ADV":
							descriptor += child.text + " "
					descriptor += adjective.text

					negation_tag = self.find_negation_tag(adjective)


					#Direct (i.e. The dress has a beautiful colour)
					noun = self.find_noun_head(adjective)
					if noun.pos_ == "NOUN" or noun.pos_ == "PRON":
						trace = f"Direct Reference Detected for Adjective: {adjective}"
						for chunk in sent.noun_chunks:
							if chunk.root == noun and adjective not in chunk:
								isFound = True
								noun_subj = chunk
							else:
								isFound = True
								noun_subj = noun             

					#Passive Voice (i.e. Colour of the dress was beautiful)
					elif adjective.head.pos_ == "AUX" or adjective.head.pos_ == "VERB":
						trace = f"Indirect Reference Detected for Adjective: {adjective}"
						for child in adjective.head.children:
							if child.pos_ == "NOUN" or child.pos_ == "PRON":
								noun = child                      
								for chunk in sent.noun_chunks:
									if chunk.root == child and adjective not in chunk:
										isFound = True
										noun_subj = chunk
									else:
										isFound = True
										noun_subj = noun
										
					#Guessing when improper grammer is used (i.e. Colour of the dress was beautiful vs also dress colour beautiful)
					else:
						trace = f"Finding noun subject for Adjective: {adjective}\n"
						start = self.find_span_start(sent, adjective)
						end = self.find_span_end(sent, adjective)
						extract = sent[start:end]
						trace += f"Extract: {extract}\n"

						for token in extract:
							if token.pos_ == "NOUN" and token.dep_ == "nsubj":
								isFound = True
								noun_subj = token
							if token.dep_ == "neg":
								negation_tag = True
				except:
					isFound = False

				if isFound:
					topic = self.match_topics(noun, adjective, self.topic_list, self.noun_keywords, self.adjective_keywords)
				else:
					trace += f"Matching adjective without noun for Adjective: {adjective}"
					noun_subj = None
					topic = self.match_topics(self.nlp("I")[0], adjective, self.topic_list, self.noun_keywords, self.adjective_keywords)

				if topic != None:
					if noun_subj == None:                    
						if SENTI_MODEL == 'logreg':
							prediction = self.SA_TOAD.logreg_model(str(descriptor) + " " + str(topic), negation_tag)
						elif SENTI_MODEL == 'svm':
							prediction = self.SA_TOAD.SVM_model(str(descriptor) + " " + str(topic), negation_tag)
						elif SENTI_MODEL == 'spacy':
							prediction = self.SA_TOAD.spacy_model(str(descriptor) + " " + str(topic), negation_tag)
					else:
						if SENTI_MODEL == 'logreg':
							prediction = self.SA_TOAD.logreg_model(str(descriptor) + " " + str(noun_subj), negation_tag)
						elif SENTI_MODEL == 'svm':
							prediction = self.SA_TOAD.SVM_model(str(descriptor) + " " + str(noun_subj), negation_tag)
						elif SENTI_MODEL == 'spacy':
							prediction = self.SA_TOAD.spacy_model(str(descriptor) + " " + str(noun_subj), negation_tag)
						

					descriptor_pair.append((descriptor, noun_subj, negation_tag, topic, prediction))

				if DEBUG:
					print(f"Trace: {trace}")
					if topic != None:
						print(f"Descriptor_pair: {(descriptor, noun_subj, negation_tag, topic, prediction)}")
					print("")

		if DEBUG:
			print(f"All descriptor_pair: {descriptor_pair}")
			print("")
		
		for pair in descriptor_pair:
			topic_total[pair[3]] += 1
			if pair[4] == "Positive":
				topic_positive[pair[3]] += 1
				
		for topic in self.topic_list:
			if topic_total[topic] != 0 and (topic_positive[topic] / topic_total[topic]) >= 0.5:
				topic_prediction[topic] = "Positive"
			elif topic_total[topic] != 0 and (topic_positive[topic] / topic_total[topic]) < 0.5:
				topic_prediction[topic] = "Negative"
			else:
				topic_prediction[topic] = None


		print(f"Review: {review}")
		print(f"Topic_prediction: {topic_prediction}")
		print("---------------------------------------------------------------")
		print("")
		
		return topic_prediction

if __name__ == "__main__":

	DEBUG = True
	SENTI_MODEL = "spacy"
	review1 = "It was a very beautiful dress"
	review2 = "The maxi dress was very beautiful"
	review3 = "Very beautiful"
	review4 = "The dress is very pretty, but it runs very small in the waist and very large in the bust. If you're not an extreme hour-glass, be prepared to alter this before wearing it. I'm short, so I plan to take some fabric either from the hem or the oversized bust to redistribute as needed, personally. Not as comfortable as some of the other items I've gotten from SheIn before - the fabric is a little scratchier than anticipated - but it does flow nicely when you move around."

	rule_based_ADSA = Rule_Based_ADSA()
	print(rule_based_ADSA.rule_based_ADSA_model(review1, DEBUG = DEBUG, SENTI_MODEL = SENTI_MODEL))
	print("---------------------------------------------------------------")
	print(rule_based_ADSA.rule_based_ADSA_model(review2, DEBUG = DEBUG, SENTI_MODEL = SENTI_MODEL))
	print("---------------------------------------------------------------")
	print(rule_based_ADSA.rule_based_ADSA_model(review3, DEBUG = DEBUG, SENTI_MODEL = SENTI_MODEL))
	print("---------------------------------------------------------------")
	print(rule_based_ADSA.rule_based_ADSA_model(review4, DEBUG = DEBUG, SENTI_MODEL = SENTI_MODEL))
	print("---------------------------------------------------------------")