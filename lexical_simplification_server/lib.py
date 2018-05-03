import re
import socket
import urllib2 as urllib
import nltk
import kenlm
import codecs
import os
import pickle
import gensim
import unittest
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.stem import SnowballStemmer
from nltk.corpus import wordnet as wn
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn import linear_model
from keras.models import *
import numpy as np

################################################ COMPLEX WORD IDENTIFIERS #######################################################

class EnglishComplexWordIdentifier:

	def __init__(self, freq_map, mean_freq, std_freq, min_proportion):
		self.freq_map = freq_map
		self.mean_freq = mean_freq
		self.std_freq = std_freq
		self.min_proportion = min_proportion

	def getSimplifiability(self, target):
		#Try to get a list of synonyms for the target from WordNet:
		try:
			lemma = wn.morphy(target)
			syns = wn.synsets(lemma)
			synonyms = set([])
			for syn in syns:
				synonyms.update([s.strip() for s in syn.lemma_names() if '_' not in s])
			if lemma in synonyms:
				synonyms.remove(lemma)
		except Exception:
			synonyms = set([])
		
		#Get the target's frequency:
		if isinstance(target, unicode):
			word = target.encode('utf8')
		else:
			word = target
		word_freq = 0
		if word.lower() in self.freq_map:
			word_freq = self.freq_map[word.lower()]

		#Check wether frequency is small enough and there are existing synonyms:
		if word_freq<=self.mean_freq/self.min_proportion and len(synonyms)>0:
			return True
		else:
			return False

















########################################################## SUBSTITUTION GENERATORS ###############################################

class SIMPATICOGenerator:

	def __init__(self, posw2vmodel, stemmer=None, prohibited_edges=set([]), prohibited_chars=set([]), tag_class_func=lambda x: x):
		self.model = gensim.models.KeyedVectors.load_word2vec_format(posw2vmodel, binary=True, unicode_errors='ignore')
		self.stemmer = stemmer
		self.prohibited_edges = prohibited_edges
		self.prohibited_chars = prohibited_chars
		self.tag_class_func = tag_class_func

	def getSubstitutionsSingle(self, sentence, target, index, tagged_sents, amount):
		#If target is a word:
		if ' ' not in target:
			substitutions = self.getInitialSetForWords([[sentence, target, index]], tagged_sents, amount)
		#If target is a phrase:
		else:
			substitutions = self.getInitialSetForPhrases([[sentence, target, index]], tagged_sents, amount)
		return substitutions

	def getInitialSetForWords(self, data, tsents, amount):
		trgs = []
		trgsstems = []
		for i in range(0, len(data)):
			d = data[i]
			tags = tsents[i]
			target = d[1].strip().lower()
			head = int(d[2].strip())
			tag = self.tag_class_func(tags[head][1])
			trgs.append(target)
		trgsstems = self.stemWords(trgs)
		trgmap = {}
		for i in range(0, len(trgsstems)):
			target = data[i][1].strip().lower()
			head = int(data[i][2].strip())
			tag = self.tag_class_func(tsents[i][head][1])
			stem = trgsstems[i]
			trgmap[target] = stem

		subs = []
		cands = set([])
		for i in range(0, len(data)):
			d = data[i]

			t = trgs[i]
			tstem = trgsstems[i]

			tags = tsents[i]
			head = int(d[2].strip())
			tag = tags[head][1]

			word = t + '|||' + self.tag_class_func(tag)

			most_sim = []
			try:
				most_sim = self.model.most_similar(positive=[word], topn=50)
			except KeyError:
				most_sim = []
			newcands = [word[0] for word in most_sim if '_' not in word[0] and '|||' in word[0]]
			subs.append(newcands)
			cands.update([cand.split('|||')[0] for cand in newcands])

		cands = list(cands)
		candsstems = self.stemWords(cands)
		candmap = {}
		for i in range(0, len(cands)):
			cand = cands[i]
			stem = candsstems[i]
			candmap[cand] = stem

		subs_filtered = self.filterSubsForWords(data, tsents, subs, candmap, trgs, trgsstems)

		final_cands = {}
		for i in range(0, len(data)):
			target = data[i][1]
			cands = subs_filtered[i][0:min(amount, subs_filtered[i])]
			cands = [word.split('|||')[0].strip() for word in cands]
			if target not in final_cands:
				final_cands[target] = set([])
			final_cands[target].update(set(cands))

		return final_cands

	def filterSubsForWords(self, data, tsents, subs, candmap, trgs, trgsstems):
		result = []
		for i in range(0, len(data)):
			d = data[i]

			t = trgs[i]
			tstem = trgsstems[i]

			tags = tsents[i]
			head = int(d[2].strip())
			tag = self.tag_class_func(tags[head][1])

			word = t + '|||' + self.tag_class_func(tag)

			most_sim = subs[i]
			most_simf = []

			for cand in most_sim:
				candd = cand.split('|||')
				cword = candd[0].strip()
				ctag = candd[1].strip()
				cstem = candmap[cword]

				if ctag == tag:
					if cstem != tstem:
						if cword not in t and t not in cword:
							most_simf.append(cand)

			result.append(most_simf)
		return result

	def getInitialSetForPhrases(self, data, tsents, amount):
		subs = []
		cands = set([])
		for i in range(0, len(data)):
			d = data[i]

			target = d[1].replace(' ', '_')
			head = int(d[2].strip())			
			target_words = self.phraseToWords(target, head, tsents[i])

			most_sim = []
			try:
				most_sim = self.model.most_similar(positive=[target], topn=50)
			except KeyError:
				most_sim = self.simplifyIndividualPhraseWords(target_words)
				print 'It worked: ', most_sim

			subs.append([w[0] for w in most_sim])

		subs_filtered = self.filterSubsForPhrases(data, subs)
				
		final_cands = {}
		for i in range(0, len(data)):
			target = data[i][1]
			cands = subs_filtered[i][0:min(amount, subs_filtered[i])]
			if target not in final_cands:
				final_cands[target] = set([])
			final_cands[target].update(set(cands))

		return final_cands
				
	def filterSubsForPhrases(self, data, subs):
		result = []

		vowels = set('aeiouyw')
		consonants = set('bcdfghjklmnpqrstvxz')

		for i in range(0, len(data)):
			d = data[i]

			sent = d[0].split(' ')
			index = int(d[2])
			if index==0:
				prevtgt = 'NULL'
			else:
				prevtgt = sent[index-1]
			if index==len(sent)-1:
				proxtgt = 'NULL'
			else:
				proxtgt = sent[index+1]
								
			target = d[1]
			targett = target.split(' ')
			firsttgt = targett[0]
			lasttgt = targett[-1]

			most_sim = subs[i]
			most_simf = []

			for cand in most_sim:
				c = cand.replace('_', ' ')
				if '|||' in c:
					c = c.split('|||')[0]
				tokens = c.split(' ')
				first = tokens[0]
				last = tokens[-1]
				cchars = set(c)
				edges = set([first, last])
				inter_edge = edges.intersection(self.prohibited_edges)
				inter_chars = cchars.intersection(self.prohibited_chars)
				if c not in target and target not in c and first!=prevtgt and last!=proxtgt:
					if len(inter_edge)==0 and len(inter_chars)==0:
						if (firsttgt=='most' and first!='more') or (firsttgt=='more' and first!='most') or (firsttgt!='more' and firsttgt!='most'):
							if (prevtgt=='an' and c[0] in vowels) or (prevtgt=='a' and c[0] in consonants) or (prevtgt!='an' and prevtgt!='a'):
								most_simf.append(c)

			result.append(most_simf)
		return result

	def simplifyIndividualPhraseWords(self, words):
		canBeSimplified = True
		for word in words:
			if word not in self.model.vocab:
				canBeSimplified = False
		if canBeSimplified:
			candmap = {}
			for word in words:
				candmap[word] = [w[0].split('|||')[0] for w in self.model.most_similar(positive=[word], topn=5)]
			candset = set(candmap[words[0]])
			for word in words[1:]:
				cands = candmap[word]
				newset = set([])
				for c1 in candset:
					for c2 in cands:
						newset.add(c1+'_'+c2)
				candset = newset
			return [(w, '_') for w in list(candset)]
		else:
			return []

	def phraseToWords(self, target, head, tags):
		result = []
		words = target.split('_')
		for i in range(0, len(words)):
			word = words[i]
			index = head+i
			tag = self.tag_class_func(tags[index][1])
			result.append(word+'|||'+tag)
		return result

	def stemWords(self, words):
		result = []
		for word in words:
			if self.stemmer:
				result.append(self.stemmer.stem(word))
			else:
				result.append(word)
		return result

























############################################################# SUBSTITUTION SELECTORS ##############################################

class BoundaryRanker:

	def __init__(self, fe):
		self.fe = fe
		self.classifier = None
		self.feature_selector = None

	def trainRankerWithCrossValidation(self, victor_corpus, positive_range, folds, test_size, losses=['hinge', 'modified_huber'], penalties=['elasticnet'], alphas=[0.0001, 0.001, 0.01], l1_ratios=[0.0, 0.15, 0.25, 0.5, 0.75, 1.0], k='all'):
		# Read victor corpus:
		data = []
		f = open(victor_corpus)
		for line in f:
			data.append(line.strip().split('\t'))
		f.close()

		# Create matrixes:
		X = self.fe.calculateFeatures(victor_corpus)
		Y = self.generateLabels(data, positive_range)

		# Select features:
		self.feature_selector = SelectKBest(f_classif, k=k)
		self.feature_selector.fit(X, Y)
		X = self.feature_selector.transform(X)

		# Extract ranking problems:
		firsts = []
		candidates = []
		Xsets = []
		Ysets = []
		index = -1
		for line in data:
			fs = set([])
			cs = []
			Xs = []
			Ys = []
			for cand in line[3:len(line)]:
				index += 1
				candd = cand.split(':')
				rank = candd[0].strip()
				word = candd[1].strip()

				cs.append(word)
				Xs.append(X[index])
				Ys.append(Y[index])
				if rank == '1':
					fs.add(word)
			firsts.append(fs)
			candidates.append(cs)
			Xsets.append(Xs)
			Ysets.append(Ys)

		# Create data splits:
		datasets = []
		for i in range(0, folds):
			Xtr, Xte, Ytr, Yte, Ftr, Fte, Ctr, Cte = train_test_split(
				Xsets, Ysets, firsts, candidates, test_size=test_size, random_state=i)
			Xtra = []
			for matrix in Xtr:
				Xtra += matrix
			Xtea = []
			for matrix in Xte:
				Xtea += matrix
			Ytra = []
			for matrix in Ytr:
				Ytra += matrix
			datasets.append((Xtra, Ytra, Xte, Xtea, Fte, Cte))

		# Get classifier with best parameters:
		max_score = -1.0
		parameters = ()
		for l in losses:
			for p in penalties:
				for a in alphas:
					for r in l1_ratios:
						sum = 0.0
						sum_total = 0
						for dataset in datasets:
							Xtra = dataset[0]
							Ytra = dataset[1]
							Xte = dataset[2]
							Xtea = dataset[3]
							Fte = dataset[4]
							Cte = dataset[5]

							classifier = linear_model.SGDClassifier(
								loss=l, penalty=p, alpha=a, l1_ratio=r, epsilon=0.0001)
							try:
								classifier.fit(Xtra, Ytra)
								t1 = self.getCrossValidationScore(
									classifier, Xtea, Xte, Fte, Cte)
								sum += t1
								sum_total += 1
							except Exception:
								pass
						sum_total = max(1, sum_total)
						if (sum / sum_total) > max_score:
							max_score = sum
							parameters = (l, p, a, r)
		self.classifier = linear_model.SGDClassifier(
			loss=parameters[0], penalty=parameters[1], alpha=parameters[2], l1_ratio=parameters[3], epsilon=0.0001)
		self.classifier.fit(X, Y)

	def getCrossValidationScore(self, classifier, Xtea, Xte, firsts, candidates):
		distances = classifier.decision_function(Xtea)
		index = -1
		corrects = 0
		total = 0
		for i in range(0, len(Xte)):
			xset = Xte[i]
			maxd = -999999
			for j in range(0, len(xset)):
				index += 1
				distance = distances[index]
				if distance > maxd:
					maxd = distance
					maxc = candidates[i][j]
			if maxc in firsts[i]:
				corrects += 1
			total += 1
		return float(corrects) / float(total)

	def getRankings(self, data):
		# Transform data:
		textdata = ''
		for inst in data:
			for token in inst:
				textdata += token + '\t'
			textdata += '\n'
		textdata = textdata.strip()

		# Create matrixes:
		X = self.fe.calculateFeatures(textdata, input='text')

		# Select features:
		X = self.feature_selector.transform(X)

		# Get boundary distances:
		distances = self.classifier.decision_function(X)

		# Get rankings:
		result = []
		index = 0
		for i in range(0, len(data)):
			line = data[i]
			scores = {}
			for subst in line[3:len(line)]:
				word = subst.strip().split(':')[1].strip()
				scores[word] = distances[index]
				index += 1
			ranking_data = sorted(
				scores.keys(), key=scores.__getitem__, reverse=True)
			result.append(ranking_data)

		# Return rankings:
		return result

	def generateLabels(self, data, positive_range):
		Y = []
		for line in data:
			max_range = min(
				int(line[len(line) - 1].split(':')[0].strip()), positive_range)
			for i in range(3, len(line)):
				rank_index = int(line[i].split(':')[0].strip())
				if rank_index <= max_range:
					Y.append(1)
				else:
					Y.append(0)
		return Y


class BoundarySelector:

	def __init__(self, boundary_ranker):
		self.ranker = boundary_ranker

	def trainSelectorWithCrossValidation(self, victor_corpus, positive_range, folds, test_size, losses=['hinge', 'modified_huber'], penalties=['elasticnet'], alphas=[0.0001, 0.001, 0.01], l1_ratios=[0.0, 0.15, 0.25, 0.5, 0.75, 1.0], k='all'):
		self.ranker.trainRankerWithCrossValidation(
			victor_corpus, positive_range, folds, test_size, losses=losses, penalties=penalties, alphas=alphas, l1_ratios=l1_ratios, k=k)

	def selectCandidates(self, data, proportion, proportion_type='percentage'):
		rankings = self.ranker.getRankings(data)

		selected_substitutions = []

		index = -1
		for line in data:
			index += 1

			selected_candidates = None
			if proportion_type == 'percentage':
				toselect = None
				if proportion > 1.0:
					toselect = 1.0
				else:
					toselect = proportion
				selected_candidates = rankings[index][0:max(
					1, int(toselect * float(len(rankings[index]))))]
			else:
				toselect = None
				if proportion < 1:
					toselect = 1
				elif proportion > len(rankings[index]):
					toselect = len(rankings[index])
				else:
					toselect = proportion
				selected_candidates = rankings[index][0:toselect]

			selected_substitutions.append(selected_candidates)

		return selected_substitutions





###############################################################  SUBSTITUTION RANKERS #########################################################

class GlavasRanker:

	def __init__(self, fe):
		"""
		Creates an instance of the GlavasRanker class.

		@param fe: A configured FeatureEstimator object.
		"""

		self.fe = fe
		self.feature_values = None

	def getRankings(self, alldata):

		# Calculate features:
		textdata = ''
		for inst in alldata:
			for token in inst:
				textdata += token + '\t'
			textdata += '\n'
		textdata = textdata.strip()
		self.feature_values = self.fe.calculateFeatures(textdata, input='text')

		# Create object for results:
		result = []

		# Read feature values for each candidate in victor corpus:
		index = 0
		for data in alldata:
			# Get all substitutions in ranking instance:
			substitutions = data[3:len(data)]

			# Get instance's feature values:
			instance_features = []
			for substitution in substitutions:
				instance_features.append(self.feature_values[index])
				index += 1

			rankings = {}
			for i in range(0, len(self.fe.identifiers)):
				# Create dictionary of substitution to feature value:
				scores = {}
				for j in range(0, len(substitutions)):
					substitution = substitutions[j]
					word = substitution.strip().split(':')[1].strip()
					scores[word] = instance_features[j][i]

				# Check if feature is simplicity or complexity measure:
				rev = False
				if self.fe.identifiers[i][1] == 'Simplicity':
					rev = True

				# Sort substitutions:
				words = scores.keys()
				sorted_substitutions = sorted(
					words, key=scores.__getitem__, reverse=rev)

				# Update rankings:
				for j in range(0, len(sorted_substitutions)):
					word = sorted_substitutions[j]
					if word in rankings:
						rankings[word] += j
					else:
						rankings[word] = j

			# Produce final rankings:
			final_rankings = sorted(rankings.keys(), key=rankings.__getitem__)

			# Add them to result:
			result.append(final_rankings)

		# Return result:
		return result


class NNRegressionRanker:

	def __init__(self, fe, model):
		self.fe = fe
		self.model = model
		
	def getRankings(self, data):
		#Transform data:
		textdata = ''
		for inst in data:
			for token in inst:
				textdata += token+'\t'
			textdata += '\n'
		textdata = textdata.strip()
		
		#Create matrix:
		features = self.fe.calculateFeatures(textdata, input='text')
		
		ranks = []
		c = -1
		for line in data:
			cands = [cand.strip().split(':')[1].strip() for cand in line[3:]]
			featmap = {}
			scoremap = {}
			for cand in cands:
				c += 1
				featmap[cand] = features[c]
				scoremap[cand] = 0.0
			for i in range(0, len(cands)-1):
				cand1 = cands[i]
				for j in range(i+1, len(cands)):
					cand2 = cands[j]
					posneg = np.concatenate((featmap[cand1], featmap[cand2]))
					probs = self.model.predict(np.array([posneg]))
					score = probs[0]
					scoremap[cand1] += score
					negpos = np.concatenate((featmap[cand2], featmap[cand1]))
					probs = self.model.predict(np.array([negpos]))
					score = probs[0]
					scoremap[cand1] -= score
			rank = sorted(scoremap.keys(), key=scoremap.__getitem__, reverse=True)
			if len(rank)>1:
				if rank[0]==line[1].strip():
					rank = rank[1:]
			ranks.append(rank)
		return ranks




####################################################################### TAG TRANSFORMATION FUNCTIONS  ###################################################################

def EnglishGetTagClass(tag):
	result = None
	if tag.startswith('N'):
		result = 'N'
	elif tag.startswith('V'):
		result = 'V'
	elif tag.startswith('RB'):
		result = 'A'
	elif tag.startswith('J'):
		result = 'J'
	elif tag.startswith('W'):
		result = 'W'
	elif tag.startswith('PRP'):
		result = 'P'
	else:
		result = tag.strip()
	return result

def SpanishGetTagClass(tag):
	targets = set('anprv')
	if tag.startswith('np'):
		return tag
	else:
		if tag[0] in targets:
			return tag[0]
		else:
			return tag

def GalicianGetTagClass(tag):
        return tag

def ItalianGetTagClass(tag):
	return tag







