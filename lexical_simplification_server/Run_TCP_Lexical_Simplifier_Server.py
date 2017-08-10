from lib import *
from lexenstein.morphadorner import *
from lexenstein.spelling import *
from lexenstein.features import *
from langdetect import detect
import socket

#Classes:
class MultilingualLexicalSimplifier:

	def __init__(self, embeddingsgen, selector, ranker):
		self.embeddingsgen = embeddingsgen
		self.selector = selector
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
	
	def selectCandidates(self, data):		
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
		
class EnhancedLexicalSimplifier:

	def __init__(self, dictgen, embeddingsgen, selector, ranker):
		self.dictgen = dictgen
		self.embeddingsgen = embeddingsgen
		self.selector = selector
		self.ranker = ranker
		
	def generateCandidates(self, sent, target, index, tagged_sents):
		#Produce candidates based on dictionary map:
		if target not in self.dictgen:
			subs = self.embeddingsgen.getSubstitutionsSingle(sent, target, index, tagged_sents, 10)
		else:
			subs = self.embeddingsgen.getSubstitutionsSingle(sent, target, index, tagged_sents, 3)

		#Create input data instance:
		fulldata = [sent, target, index]
		for sub in subs[target]:
			fulldata.append('0:'+sub)
		if target in self.dictgen:
			for sub in self.dictgen[target]:
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
def getTaggedSentences(sents, configurations, lang):
	tagged_sents = []
	for sent in sents:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect(("localhost", int(configurations[lang+'_stanford_tagger_port'])))
		sinput = sent+'\n'
		s.send(sinput.encode("utf-8"))
		resp = [token.split(r'_') for token in s.recv(2014).decode('utf-8').strip().split(' ')]
		resp = [(token[0], token[1]) for token in resp]
		tagged_sents.append(resp)
	print tagged_sents
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

def loadResources(path):
	#Open resource file:
	f = open(path)
	
	#Create resource map:
	resources = {}
	
	#Read resource paths:
	for line in f:
		data = line.strip().split('\t')
		if data[0] in resources:
			print 'Repeated resource name: ' + data[0] + '. Please change the name of this resource.'
		resources[data[0]] = data[1]
	f.close()
	
	#Return resource database:
	return resources

def getSpanishLexicalSimplifier(resources):
	#General purpose:
	victor_corpus = resources['spanish_ubr']
	w2vpm_spa = resources['spa_caretro_embeddings']
	w2vty_spa = resources['spa_typical_embeddings']

	#Generator:
	kg = SpanishTaggedGenerator(w2vpm_spa)

	#Selector:
	fe = FeatureEstimator()
	fe.addCollocationalFeature(resources['spa_lm'], 2, 2, 'Complexity')
	fe.addWordVectorSimilarityFeature(w2vty_spa, 'Simplicity')
	br = BoundaryRanker(fe)
	bs = BoundarySelector(br)
	bs.trainSelectorWithCrossValidation(resources['spanish_ubr'], 1, 5, 0.25, k='all')

	#Ranker:
	fe = FeatureEstimator()
	fe.addLengthFeature('Complexity')
	fe.addCollocationalFeature(resources['spa_lm'], 2, 2, 'Simplicity')
	gr = GlavasRanker(fe)

	#Return LexicalSimplifier object:
	return EnhancedLexicalSimplifier({}, kg, bs, gr)
	
def getEnglishLexicalSimplifier(resources):
	#General purpose:
	nc = NorvigCorrector(resources['norvig_corrector'], format='bin')
	victor_corpus = resources['nnseval']
	w2vpm_eng = resources['eng_caretro_embeddings']
	w2vty_eng = resources['eng_typical_embeddings']

	#Generator:
	ng = getNewselaCandidates(resources['newsela_candidates'])
	kg = PaetzoldGenerator(w2vpm_eng, nc)

	#Selector:
	fe = FeatureEstimator()
	fe.addCollocationalFeature(resources['eng_sub_lm'], 2, 2, 'Complexity')
	fe.addWordVectorSimilarityFeature(w2vty_eng, 'Simplicity')
	br = BoundaryRanker(fe)
	bs = BoundarySelector(br)
	bs.trainSelectorWithCrossValidation(victor_corpus, 2, 5, 0.25, k='all')

	#Ranker:
	fe = FeatureEstimator(norm=False)
	fe.addCollocationalFeature(resources['eng_sub_lm'], 2, 2, 'Simplicity')
	model_file = resources['nn_sr_model']
	model = model_from_json(open(model_file+'.json').read())
	model.load_weights(model_file+'.h5')
	model.compile(loss='mean_squared_error', optimizer='adam')
	nr = NNRegressionRanker(fe, model)
	
	#Return LexicalSimplifier object:
	return EnhancedLexicalSimplifier(ng, kg, bs, nr)

def getGalicianLexicalSimplifier(resources):
	#General purpose:
	w2vpm_gal = resources['gal_embeddings']

	#Generator:
	gg = MultilingualGlavasGenerator(w2vpm_gal, 'spanish')
	
	#Selector:
	fe = FeatureEstimator()
	fe.resources[w2vpm_gal] = gg.model
	fe.addCollocationalFeature(resources['gal_lm'], 2, 2, 'Complexity')
	fe.addWordVectorSimilarityFeature(w2vpm_gal, 'Simplicity')
	br = BoundaryRanker(fe)
	bs = BoundarySelector(br)
	bs.trainSelectorWithCrossValidation(resources['galician_ubr'], 1, 5, 0.25, k='all')

	#Ranker:
	fe = FeatureEstimator()
	fe.addLengthFeature('Complexity')
	fe.addCollocationalFeature(resources['gal_lm'], 2, 2, 'Simplicity')
	gr = GlavasRanker(fe)
	
	#Return LexicalSimplifier object:
	return MultilingualLexicalSimplifier(gg, bs, gr)
	
def getItalianLexicalSimplifier(resources):
	#General purpose:
	w2vpm_ita = resources['ita_embeddings']

	#Generator:
	gg = MultilingualGlavasGenerator(w2vpm_ita, 'italian')
	
	#Selector:
	fe = FeatureEstimator()
	fe.resources[w2vpm_ita] = gg.model
	fe.addCollocationalFeature(resources['ita_lm'], 2, 2, 'Complexity')
	fe.addWordVectorSimilarityFeature(w2vpm_ita, 'Simplicity')
	br = BoundaryRanker(fe)
	bs = BoundarySelector(br)
	bs.trainSelectorWithCrossValidation(resources['italian_ubr'], 1, 5, 0.25, k='all')

	#Ranker:
	fe = FeatureEstimator()
	fe.addLengthFeature('Complexity')
	fe.addCollocationalFeature(resources['ita_lm'], 2, 2, 'Simplicity')
	gr = GlavasRanker(fe)
	
	#Return LexicalSimplifier object:
	return MultilingualLexicalSimplifier(gg, bs, gr)
		
	
################################################ MAIN ########################################################	

#Load global resources and configurations:
configurations = loadResources('../configurations.txt')
resources = loadResources('../resources.txt')

#Load English simplifier:
simplifier_eng = getEnglishLexicalSimplifier(resources)
simplifier_gal = getGalicianLexicalSimplifier(resources)
simplifier_ita = getItalianLexicalSimplifier(resources)
simplifier_spa = getSpanishLexicalSimplifier(resources)

#Wait for simplification requests:
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', int(configurations['ls_local_server_port'])))
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
	if 1:
	#try:
		if lang=='en':
			#Tag sentence:
			tagged_sents = getTaggedSentences([sent], configurations, lang)
			#Update request information:
			sent, index = updateRequest(sent, target, int(index), tagged_sents[0])
			#SG:
			sg_output = simplifier_eng.generateCandidates(sent, target, index, tagged_sents)
			#SS:
			ss_output = simplifier_eng.selectCandidates(sg_output, tagged_sents)
			#SR:
			sr_output = simplifier_eng.rankCandidates(ss_output)
		elif lang=='it':
			#SG:
			sg_output = simplifier_ita.generateCandidates(sent, target, index)
			#SS:
			ss_output = simplifier_ita.selectCandidates(sg_output)
			#SR:
			sr_output = simplifier_ita.rankCandidates(ss_output)
		elif lang=='es':
			#Tag sentence:
			tagged_sents = getTaggedSentences([sent], configurations, lang)
			#Update request information:
			sent, index = updateRequest(sent, target, int(index), tagged_sents[0])
			#SG:
			sg_output = simplifier_spa.generateCandidates(sent, target, index, tagged_sents)
			#SS:
			ss_output = simplifier_spa.selectCandidates(sg_output, tagged_sents)
			#SR:
			sr_output = simplifier_spa.rankCandidates(ss_output)
		else:
			#SG:
			sg_output = simplifier_gal.generateCandidates(sent, target, index)
			#SS:
			ss_output = simplifier_gal.selectCandidates(sg_output)
			#SR:
			sr_output = simplifier_gal.rankCandidates(ss_output)
	#except Exception:
	#	sr_output = [[]]

	#Get final replacement:
	replacement = 'NULL'
	if len(sr_output[0])>0:
		try:
			replacement = sr_output[0][0].encode('utf8')
		except Exception:
			replacement = sr_output[0][0]

	#Send result:
	try:
		conn.send(replacement+'\n')
		conn.close()
	except Exception:
		conn.send('NULL\n')
		conn.close()
