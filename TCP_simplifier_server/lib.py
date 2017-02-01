import xml.etree.ElementTree as ET
import re, socket
import urllib2 as urllib
from nltk.corpus import wordnet as wn
import subprocess
import nltk
from nltk.tag.stanford import StanfordPOSTagger
import kenlm
import codecs
import os, pickle
import gensim
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.stem import SnowballStemmer
from sklearn.cross_validation import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn import linear_model
from keras.models import *
import numpy as np

class GalicianGlavasGeneratorBetter:

	def __init__(self, w2vmodel):
		self.lemmatizer = WordNetLemmatizer()
		self.stemmer = SnowballStemmer("spanish")
		self.model = gensim.models.word2vec.Word2Vec.load_word2vec_format(w2vmodel, binary=True, unicode_errors='ignore')
		
	def getSubstitutionsSingle(self, sentence, target, index, amount):
		substitutions = self.getInitialSet([[sentence, target, index]], amount)
		return substitutions

	def getInitialSet(self, data, amount):
		trgs = []
		trgsstems = []
		trgslemmas = []
		for i in range(0, len(data)):
			d = data[i]
			target = d[1].strip().lower()
			head = int(d[2].strip())
			trgs.append(target)
		trgslemmas = self.lemmatizeWords(trgs)
		trgsstems = self.stemWords(trgs)

		trgmap = {}
		for i in range(0, len(trgslemmas)):
			target = data[i][1].strip().lower()
			head = int(data[i][2].strip())
			lemma = trgslemmas[i]
			stem = trgsstems[i]
			trgmap[target] = (lemma, stem)

		subs = []
		cands = set([])
		for i in range(0, len(data)):
			d = data[i]

			t = trgs[i]
			tstem = trgsstems[i]
			tlemma = trgslemmas[i]

			word = t

			most_sim = []
			try:
				most_sim = self.model.most_similar(positive=[word.decode('utf-8')], topn=50)
			except KeyError:
				most_sim = []

			subs.append([word[0] for word in most_sim])

		subsr = subs
		subs = []
		for l in subsr:
			lr = []
			for inst in l:
				cand = inst.split('|||')[0].strip()
				cands.add(cand)
				lr.append(inst)
			subs.append(lr)

		cands = list(cands)
		candslemmas = self.lemmatizeWords(cands)
		candsstems = self.stemWords(cands)
		candmap = {}
		for i in range(0, len(cands)):
			cand = cands[i]
			lemma = candslemmas[i]
			stem = candsstems[i]
			candmap[cand] = (lemma, stem)

		subs_filtered = self.filterSubs(data, subs, candmap, trgs, trgsstems, trgslemmas)

		final_cands = {}
		for i in range(0, len(data)):
			target = data[i][1]
			cands = subs_filtered[i][0:min(amount, subs_filtered[i])]
			cands = [word.split('|||')[0].strip() for word in cands]
			if target not in final_cands:
				final_cands[target] = set([])
			final_cands[target].update(set(cands))

		return final_cands
				
	def lemmatizeWords(self, words):
		result = []
		for word in words:
			try:
				result.append(self.lemmatizer.lemmatize(word))
			except Exception:
				result.append(word)
		return result

	def stemWords(self, words):
		result = []
		for word in words:
			try:
				result.append(self.stemmer.stem(word))
			except Exception:
				result.append(word)
		return result
				
	def filterSubs(self, data, subs, candmap, trgs, trgsstems, trgslemmas):
		result = []
		for i in range(0, len(data)):
			d = data[i]

			t = trgs[i]
			tstem = trgsstems[i]
			tlemma = trgslemmas[i]

			word = t

			most_sim = subs[i]
			most_simf = []

			for cand in most_sim:
				cword = cand
				clemma = candmap[cword][0]
				cstem = candmap[cword][1]

				if cstem.decode('utf-8')!=tstem.decode('utf-8'):
					most_simf.append(cand)

			result.append(most_simf)
		return result

class GalicianGlavasGenerator:

	def __init__(self, w2vmodel):
		self.lemmatizer = WordNetLemmatizer()
		self.stemmer = SnowballStemmer("spanish")
		self.model = gensim.models.word2vec.Word2Vec.load_word2vec_format(w2vmodel, binary=True, unicode_errors='ignore')
		
	def getSubstitutionsSingle(self, sentence, target, index, amount):
		substitutions = self.getInitialSet([[sentence, target, index]], amount)
		return substitutions

	def getInitialSet(self, data, amount):
		trgs = []
		trgsstems = []
		trgslemmas = []
		for i in range(0, len(data)):
			d = data[i]
			target = d[1].strip().lower()
			head = int(d[2].strip())
			trgs.append(target)
		trgslemmas = self.lemmatizeWords(trgs)
		trgsstems = self.stemWords(trgs)

		trgmap = {}
		for i in range(0, len(trgslemmas)):
			target = data[i][1].strip().lower()
			head = int(data[i][2].strip())
			lemma = trgslemmas[i]
			stem = trgsstems[i]
			trgmap[target] = (lemma, stem)

		subs = []
		cands = set([])
		for i in range(0, len(data)):
			d = data[i]

			t = trgs[i]
			tstem = trgsstems[i]
			tlemma = trgslemmas[i]

			word = t

			most_sim = []
			try:
				most_sim = self.model.most_similar(positive=[word.decode('utf-8')], topn=50)
			except KeyError:
				most_sim = []

			subs.append([word[0] for word in most_sim])

		subsr = subs
		subs = []
		for l in subsr:
			lr = []
			for inst in l:
				cand = inst.split('|||')[0].strip()
				encc = None
				try:
					encc = cand.encode('ascii')
				except Exception:
					encc = None
				if encc:
					cands.add(cand)
					lr.append(inst)
			subs.append(lr)

		cands = list(cands)
		candslemmas = self.lemmatizeWords(cands)
		candsstems = self.stemWords(cands)
		candmap = {}
		for i in range(0, len(cands)):
			cand = cands[i]
			lemma = candslemmas[i]
			stem = candsstems[i]
			candmap[cand] = (lemma, stem)

		subs_filtered = self.filterSubs(data, subs, candmap, trgs, trgsstems, trgslemmas)

		final_cands = {}
		for i in range(0, len(data)):
			target = data[i][1]
			cands = subs_filtered[i][0:min(amount, subs_filtered[i])]
			cands = [str(word.split('|||')[0].strip()) for word in cands]
			if target not in final_cands:
				final_cands[target] = set([])
			final_cands[target].update(set(cands))

		return final_cands
				
	def lemmatizeWords(self, words):
		result = []
		for word in words:
			try:
				result.append(self.lemmatizer.lemmatize(word))
			except Exception:
				result.append(word)
		return result

	def stemWords(self, words):
		result = []
		for word in words:
			try:
				result.append(self.stemmer.stem(word))
			except Exception:
				result.append(word)
		return result
				
	def filterSubs(self, data, subs, candmap, trgs, trgsstems, trgslemmas):
		result = []
		for i in range(0, len(data)):
			d = data[i]

			t = trgs[i]
			tstem = trgsstems[i]
			tlemma = trgslemmas[i]

			word = t

			most_sim = subs[i]
			most_simf = []

			for cand in most_sim:
				cword = cand
				clemma = candmap[cword][0]
				cstem = candmap[cword][1]

				if cstem.decode('utf-8')!=tstem.decode('utf-8'):
					most_simf.append(cand)

			result.append(most_simf)
		return result





















class PaetzoldGenerator:

	def __init__(self, posw2vmodel, nc, pos_model, stanford_tagger, java_path):
		self.lemmatizer = WordNetLemmatizer()
		self.stemmer = PorterStemmer()
		self.model = gensim.models.word2vec.Word2Vec.load_word2vec_format(posw2vmodel, binary=True)
		self.nc = nc
		os.environ['JAVAHOME'] = java_path
		self.tagger = StanfordPOSTagger(pos_model, stanford_tagger)

	def getSubstitutions(self, victor_corpus, amount):
		#Get initial set of substitutions:
		lexf = open(victor_corpus)
		data = []
		for line in lexf:
			d = line.strip().split('\t')
			data.append(d)
		lexf.close()

		sents = [d[0] for d in data]
		tagged_sents = self.getParsedSentences(sents)
		substitutions = self.getInitialSet(data, tagged_sents, amount)

		return substitutions, tagged_sents

	def getSubstitutionsSingle(self, sentence, target, index, tagged_sents, amount):
		substitutions = self.getInitialSet([[sentence, target, index]], tagged_sents, amount)
		return substitutions
		
	def getParsedSentences(self, sents):
		tagged_sents = []
		for sent in sents:
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.connect(("localhost",2020))
			s.send(sent+'\n')
			resp = [token.split(r'_') for token in s.recv(2014).decode('utf-8').strip().split(' ')]
			resp = [(token[0], token[1]) for token in resp]
			
			tagged_sents.append(resp)
		
		return tagged_sents

	def getInitialSet(self, data, tsents, amount):
		trgs = []
		trgsc = []
		trgsstems = []
		trgslemmas = []
		trgscstems = []
		trgsclemmas = []
		for i in range(0, len(data)):
			d = data[i]
			tags = tsents[i]
			target = d[1].strip().lower()
			head = int(d[2].strip())
			tag = self.getClass(tags[head][1])
			targetc = self.nc.correct(target)
			trgs.append(target)
			trgsc.append(targetc)
		trgslemmas = self.lemmatizeWords(trgs)
		trgsclemmas = self.lemmatizeWords(trgsc)
		trgsstems = self.stemWords(trgs)
		trgscstems = self.stemWords(trgsc)
		trgmap = {}
		for i in range(0, len(trgslemmas)):
			target = data[i][1].strip().lower()
			head = int(data[i][2].strip())
			tag = self.getClass(tsents[i][head][1])
			lemma = trgslemmas[i]
			stem = trgsstems[i]
			trgmap[target] = (lemma, stem)
	
		subs = []
		cands = set([])
		for i in range(0, len(data)):
			d = data[i]

			t = trgs[i]
			tstem = trgsstems[i]
			tlemma = trgslemmas[i] 
			tc = trgsc[i]
			tcstem = trgscstems[i]
			tclemma = trgsclemmas[i]

			tags = tsents[i]
			head = int(d[2].strip())
			tag = tags[head][1]

			word = t+'|||'+self.getClass(tag)
			wordc = tc+'|||'+self.getClass(tag)

			most_sim = []
			try:
				most_sim = self.model.most_similar(positive=[word], topn=50)
			except KeyError:
				try:
					most_sim = self.model.most_similar(positive=[wordc], topn=50)
				except KeyError:
					most_sim = []
			subs.append([word[0] for word in most_sim])
			
		subsr = subs
		subs = []
		for l in subsr:
			lr = []
			for inst in l:
				cand = inst.split('|||')[0].strip()
				encc = None
				try:
					encc = cand.encode('ascii')
				except Exception:
					encc = None
				if encc:
					cands.add(cand)
					lr.append(inst)
			subs.append(lr)
			
		cands = list(cands)
		candslemmas = self.lemmatizeWords(cands)
		candsstems = self.stemWords(cands)
		candmap = {}
		for i in range(0, len(cands)):
			cand = cands[i]
			lemma = candslemmas[i]
			stem = candsstems[i]
			candmap[cand] = (lemma, stem)
		
		subs_filtered = self.filterSubs(data, tsents, subs, candmap, trgs, trgsc, trgsstems, trgscstems, trgslemmas, trgsclemmas)

		final_cands = {}
		for i in range(0, len(data)):
			target = data[i][1]
			cands = subs_filtered[i][0:min(amount, subs_filtered[i])]
			cands = [str(word.split('|||')[0].strip()) for word in cands]
			if target not in final_cands:
				final_cands[target] = set([])
			final_cands[target].update(set(cands))
		
		return final_cands
		
	def lemmatizeWords(self, words):
		result = []
		for word in words:
			result.append(self.lemmatizer.lemmatize(word))
		return result
		
	def stemWords(self, words):
		result = []
		for word in words:
			result.append(self.stemmer.stem(word))
		return result
	
	def filterSubs(self, data, tsents, subs, candmap, trgs, trgsc, trgsstems, trgscstems, trgslemmas, trgsclemmas):
		result = []
		for i in range(0, len(data)):
			d = data[i]

			t = trgs[i]
			tstem = trgsstems[i]
			tlemma = trgslemmas[i]
			tc = trgsc[i]
			tcstem = trgscstems[i]
			tclemma = trgsclemmas[i]

			tags = tsents[i]
			head = int(d[2].strip())
			tag = self.getClass(tags[head][1])

			word = t+'|||'+self.getClass(tag)
			wordc = tc+'|||'+self.getClass(tag)

			most_sim = subs[i]
			most_simf = []

			for cand in most_sim:
				candd = cand.split('|||')
				cword = candd[0].strip()
				ctag = candd[1].strip()
				clemma = candmap[cword][0]
				cstem = candmap[cword][1]

				if ctag==tag:
					if clemma!=tlemma and clemma!=tclemma and cstem!=tstem and cstem!=tcstem:
						if cword not in t and cword not in tc and t not in cword and tc not in cword:
							most_simf.append(cand)
			
			class_filtered = []
			for cand in most_simf:
				candd = cand.split('|||')
				cword = candd[0].strip()
				ctag = candd[1].strip()
				clemma = candmap[cword][0]
				cstem = candmap[cword][1]

				if tag=='V':
					if (t.endswith('ing') or tc.endswith('ing')) and cword.endswith('ing'):
						class_filtered.append(cand)
					elif (t.endswith('d') or tc.endswith('d')) and cword.endswith('d'):
						class_filtered.append(cand)
				else:
					class_filtered.append(cand)

			result.append(most_simf)
		return result
		
	def getClass(self, tag):
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




























class BoundaryRanker:

	def __init__(self, fe):
		self.fe = fe
		self.classifier = None
		self.feature_selector = None
		
	def trainRankerWithCrossValidation(self, victor_corpus, positive_range, folds, test_size, losses=['hinge', 'modified_huber'], penalties=['elasticnet'], alphas=[0.0001, 0.001, 0.01], l1_ratios=[0.0, 0.15, 0.25, 0.5, 0.75, 1.0], k='all'):
		#Read victor corpus:
		data = []
		f = open(victor_corpus)
		for line in f:
			data.append(line.strip().split('\t'))
		f.close()
		
		#Create matrixes:
		X = self.fe.calculateFeatures(victor_corpus)
		Y = self.generateLabels(data, positive_range)
		
		#Select features:
		self.feature_selector = SelectKBest(f_classif, k=k)
		self.feature_selector.fit(X, Y)
		X = self.feature_selector.transform(X)
		
		#Extract ranking problems:
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
				if rank=='1':
					fs.add(word)
			firsts.append(fs)
			candidates.append(cs)
			Xsets.append(Xs)
			Ysets.append(Ys)
		
		#Create data splits:
		datasets = []
		for i in range(0, folds):
			Xtr, Xte, Ytr, Yte, Ftr, Fte, Ctr, Cte = train_test_split(Xsets, Ysets, firsts, candidates, test_size=test_size, random_state=i)
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
		
		#Get classifier with best parameters:
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

							classifier = linear_model.SGDClassifier(loss=l, penalty=p, alpha=a, l1_ratio=r, epsilon=0.0001)
							try:
								classifier.fit(Xtra, Ytra)
								t1 = self.getCrossValidationScore(classifier, Xtea, Xte, Fte, Cte)
								sum += t1
								sum_total += 1
							except Exception:
								pass
						sum_total = max(1, sum_total)
						if (sum/sum_total)>max_score:
							max_score = sum
							parameters = (l, p, a, r)
		self.classifier = linear_model.SGDClassifier(loss=parameters[0], penalty=parameters[1], alpha=parameters[2], l1_ratio=parameters[3], epsilon=0.0001)
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
				if distance>maxd:
					maxd = distance
					maxc = candidates[i][j]
			if maxc in firsts[i]:
				corrects += 1
			total += 1
		return float(corrects)/float(total)
	
	def getRankings(self, data):
		#Transform data:
		textdata = ''
		for inst in data:
			for token in inst:
				textdata += token+'\t'
			textdata += '\n'
		textdata = textdata.strip()

		#Create matrixes:
		X = self.fe.calculateFeatures(textdata, input='text')
		
		#Select features:
		X = self.feature_selector.transform(X)
		
		#Get boundary distances:
		distances = self.classifier.decision_function(X)
		
		#Get rankings:
		result = []
		index = 0
		for i in range(0, len(data)):
			line = data[i]
			scores = {}
			for subst in line[3:len(line)]:
				word = subst.strip().split(':')[1].strip()
				scores[word] = distances[index]
				index += 1
			ranking_data = sorted(scores.keys(), key=scores.__getitem__, reverse=True)
			result.append(ranking_data)
		
		#Return rankings:
		return result

	def generateLabels(self, data, positive_range):
		Y = []
		for line in data:
			max_range = min(int(line[len(line)-1].split(':')[0].strip()), positive_range)
			for i in range(3, len(line)):
				rank_index = int(line[i].split(':')[0].strip())
				if rank_index<=max_range:
					Y.append(1)
				else:
					Y.append(0)
		return Y


























class BoundarySelector:

	def __init__(self, boundary_ranker):
		self.ranker = boundary_ranker
	
	def trainSelectorWithCrossValidation(self, victor_corpus, positive_range, folds, test_size, losses=['hinge', 'modified_huber'], penalties=['elasticnet'], alphas=[0.0001, 0.001, 0.01], l1_ratios=[0.0, 0.15, 0.25, 0.5, 0.75, 1.0], k='all'):
		self.ranker.trainRankerWithCrossValidation(victor_corpus, positive_range, folds, test_size, losses=losses, penalties=penalties, alphas=alphas, l1_ratios=l1_ratios, k=k)
		
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
				selected_candidates = rankings[index][0:max(1, int(toselect*float(len(rankings[index]))))]
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

































class GlavasRanker:

	def __init__(self, fe):
		"""
		Creates an instance of the GlavasRanker class.
	
		@param fe: A configured FeatureEstimator object.
		"""
		
		self.fe = fe
		self.feature_values = None
		
	def getRankings(self, alldata):
		
		#If feature values are not available, then estimate them:
		if self.feature_values == None:
			#Transform data:
	                textdata = ''
	                for inst in alldata:
	                        for token in inst:
	                                textdata += token+'\t'
	                        textdata += '\n'
	                textdata = textdata.strip()
			self.feature_values = self.fe.calculateFeatures(textdata, input='text')
		
		#Create object for results:
		result = []
		
		#Read feature values for each candidate in victor corpus:
		index = 0
		for data in alldata:
			#Get all substitutions in ranking instance:
			substitutions = data[3:len(data)]
			
			#Get instance's feature values:
			instance_features = []
			for substitution in substitutions:
				instance_features.append(self.feature_values[index])
				index += 1
			
			rankings = {}
			for i in range(0, len(self.fe.identifiers)):
				#Create dictionary of substitution to feature value:
				scores = {}
				for j in range(0, len(substitutions)):
					substitution = substitutions[j]
					word = substitution.strip().split(':')[1].strip()
					scores[word] = instance_features[j][i]
				
				#Check if feature is simplicity or complexity measure:
				rev = False
				if self.fe.identifiers[i][1]=='Simplicity':
					rev = True
				
				#Sort substitutions:
				words = scores.keys()
				sorted_substitutions = sorted(words, key=scores.__getitem__, reverse=rev)
				
				#Update rankings:
				for j in range(0, len(sorted_substitutions)):
					word = sorted_substitutions[j]
					if word in rankings:
						rankings[word] += j
					else:
						rankings[word] = j
		
			#Produce final rankings:
			final_rankings = sorted(rankings.keys(), key=rankings.__getitem__)
		
			#Add them to result:
			result.append(final_rankings)
		
		#Return result:
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
