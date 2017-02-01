from lib import *
from lexenstein.morphadorner import *
from lexenstein.spelling import *
from lexenstein.features import *
from langdetect import detect
import socket

#Classes:
class GalicianLexicalSimplifier:

	def __init__(self, embeddingsgen, ranker):
		self.embeddingsgen = embeddingsgen
		self.ranker = ranker
		
	def generateCandidates(self, sent, target, index):
		#Produce candidates:
		subs = self.embeddingsgen.getSubstitutionsSingle(sent, target, index, 10)

		#Create input data instance:
		fulldata = [sent, target, index]
		for sub in subs[target]:
			fulldata.append('0:'+sub)
		fulldata = [fulldata]
		
		#Return requested structures:
		return fulldata
	
	def rankCandidates(self, data):
		#Rank selected candidates:
		ranks = self.ranker.getRankings(data)
		return ranks
		
class EnglishLexicalSimplifier:

	def __init__(self, newselagen, embeddingsgen, selector, ranker):
		self.newselagen = newselagen
		self.embeddingsgen = embeddingsgen
		self.selector = selector
		self.ranker = ranker
		
	def generateCandidates(self, sent, target, index, tagged_sents):
		#Produce candidates based on Newsela map:
		if target not in self.newselagen:
			subs = self.embeddingsgen.getSubstitutionsSingle(sent, target, index, tagged_sents, 10)
		else:
			subs = self.embeddingsgen.getSubstitutionsSingle(sent, target, index, tagged_sents, 3)

		#Create input data instance:
		fulldata = [sent, target, index]
		for sub in subs[target]:
			fulldata.append('0:'+sub)
		if target in self.newselagen:
			for sub in self.newselagen[target]:
				fulldata.append('0:'+sub)
		fulldata = [fulldata]
		
		#Return requested structures:
		return fulldata
		
	def selectCandidates(self, data, tagged_sents):
		#Setup selector:
		self.selector.ranker.fe.temp_resources['tagged_sents'] = tagged_sents
		
		#If there are not enough candidates to be selected, select none:
		if len(data[0])<5:
			selected = [[]]
		else:
			selected = self.selector.selectCandidates(data, 0.5, proportion_type='percentage')		

		#Produce resulting data:
		fulldata = [data[0][0], data[0][1], data[0][2]]
		for sub in selected[0]:
			fulldata.append('0:'+sub)
		fulldata = [fulldata]
		
		#Return desired objects:
		return fulldata
	
	def rankCandidates(self, data):
		#Rank selected candidates:
		ranks = self.ranker.getRankings(data)
		return ranks

#Functions:
def getTaggedSentences(sents):
                tagged_sents = []
                for sent in sents:
                        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        s.connect(("localhost",2020))
			sinput = sent+'\n'
                        s.send(sinput.encode("utf-8"))
                        resp = [token.split(r'_') for token in s.recv(2014).decode('utf-8').strip().split(' ')]
                        resp = [(token[0], token[1]) for token in resp]
                        tagged_sents.append(resp)
                return tagged_sents

def updateRequest(sent, target, index, tagged):
	if len(sent.split(' '))==len(tagged):
		return sent, str(index)
	else:
		newsent = [t[0] for t in tagged]
		newsent = ' '.join(newsent)
		newindex = -1
		mindiff = 999999
		for i in range(0, len(tagged)):
			if tagged[i][0]==target and math.fabs(index-i)<mindiff:
				newindex = i
				mindiff = math.fabs(index-i)
		return newsent, str(newindex)

def getNewselaCandidates(file):
	subs = {}
	f = open(file)
	for line in f:
		data = line.strip().split('\t')
		target = data[0].strip()
		cands = set(data[1].strip().split('|||'))
		subs[target] = cands
	f.close()
	return subs
	
def getEnglishLexicalSimplifier():
	#General purpose:
	nc = NorvigCorrector('/export/data/ghpaetzold/LEXenstein/corpora/norvig_model_wmt.bin', format='bin')
	victor_corpus = '/export/data/ghpaetzold/benchmarking/paetzold_nns/corpora/paetzold_nns_dataset.txt'
	pos_model = '/export/data/ghpaetzold/benchmarking/lexmturk/scripts/evaluators/stanford-postagger-full-2015-04-20/models/wsj-0-18-left3words-distsim.tagger'
	stanford_tagger = '/export/data/ghpaetzold/benchmarking/lexmturk/scripts/evaluators/stanford-postagger-full-2015-04-20/stanford-postagger.jar'
	w2vpm_eng = '/export/data/ghpaetzold/word2vecvectors/models/word_vectors_all_generalized_1300_cbow_retrofitted.bin'

	#Generator:
	ng = getNewselaCandidates('/export/data/ghpaetzold/benchmarking/lseval+lexmturk/substitutions/newsela/substitutions.txt')
	kg = PaetzoldGenerator(w2vpm_eng, nc, pos_model, stanford_tagger, '/usr/bin/java')

	#Selector:
	fe = FeatureEstimator()
	fe.addCollocationalFeature('/export/data/ghpaetzold/subtitlesimdb/corpora/160715/subtleximdb.5gram.unk.bin.txt', 2, 2, 'Complexity')
	fe.addTargetPOSTagProbability('/export/data/ghpaetzold/LEXenstein/corpora/POS_condprob_model.bin', pos_model, stanford_tagger, '/usr/bin/java', 'Simplicity')
	fe.addTaggedWordVectorSimilarityFeature(w2vpm_eng, pos_model, stanford_tagger, '/usr/bin/java', 'paetzold', 'Simplicity')
	br = BoundaryRanker(fe)
	bs = BoundarySelector(br)
	bs.trainSelectorWithCrossValidation(victor_corpus, 2, 5, 0.25, k='all')

	#Ranker:
	fe = FeatureEstimator(norm=False)
	fe.addCollocationalFeature('/export/data/ghpaetzold/subimdbexperiments/corpora/binlms/subimdb', 2, 2, 'Simplicity')
	model_file = '/export/data/ghpaetzold/benchmarking/lseval+lexmturk/nnmodels/RegressionParallelNN_HIDDEN=8_LAYERS=4'
	model = model_from_json(open(model_file+'.json').read())
	model.load_weights(model_file+'.h5')
	model.compile(loss='mean_squared_error', optimizer='adam')
	nr = NNRegressionRanker(fe, model)
	
	#Return LexicalSimplifier object:
	return EnglishLexicalSimplifier(ng, kg, bs, nr)

def getGalicianLexicalSimplifier():
	#General purpose:
	w2vpm_gal = '/export/data/ghpaetzold/simpatico/simplifiers_italian_spanish/galician/corpora/galician_vectors_300_cbow.bin'

	#Generator:
	gg = GalicianGlavasGeneratorBetter(w2vpm_gal)

	#Ranker:
	fe = FeatureEstimator()
	fe.addLengthFeature('Complexity')
	fe.addCollocationalFeature('/export/data/ghpaetzold/simpatico/simplifiers_italian_spanish/galician/corpora/galician_lm.bin', 2, 2, 'Simplicity')
	gr = GlavasRanker(fe)
	
	#Return LexicalSimplifier object:
	return GalicianLexicalSimplifier(gg, gr)
	
	
	
################################################ MAIN ########################################################	
	
#Load English simplifier:
simplifier_eng = getEnglishLexicalSimplifier()
simplifier_gal = getGalicianLexicalSimplifier()

#Wait for simplification requests:
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 1414))
serversocket.listen(5)

#Upon receival of simplification request, do:
while 1:
	#Open connection:
	(conn, address) = serversocket.accept()

	#Parse request:
	data = json.loads(conn.recv(1024).decode('utf-8'))
	sent = data['sentence']
	target = data['target']
	index = data['index']
	lang = data['lang']

	#Simplify based on language:
	try:
		if lang=='en':
			#Tag sentence:
			tagged_sents = getTaggedSentences([sent])
			#Update request information:
			sent, index = updateRequest(sent, target, int(index), tagged_sents[0])
			#SG:
			sg_output = simplifier_eng.generateCandidates(sent, target, index, tagged_sents)
			#SS:
			ss_output = simplifier_eng.selectCandidates(sg_output, tagged_sents)
			#SR:
			sr_output = simplifier_eng.rankCandidates(ss_output)
		else:
			#SG:
			sg_output = simplifier_gal.generateCandidates(sent, target, index)
			#SR:
			sr_output = simplifier_gal.rankCandidates(sg_output)
	except Exception:
		sr_output = [[]]

	#Get final replacement:
	replacement = 'NULL'
	if len(sr_output[0])>0:
		replacement = sr_output[0][0]	

	#Send result:
	conn.send(replacement+'\n')
	conn.close()
