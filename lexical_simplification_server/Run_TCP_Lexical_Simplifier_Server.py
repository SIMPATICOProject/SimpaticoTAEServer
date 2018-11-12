from lib import *
from lexenstein.morphadorner import *
from lexenstein.spelling import *
from lexenstein.features import *
from langdetect import detect
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
import socket, sys, urllib2, json

#Classes:
class EnhancedLexicalSimplifier:

	def __init__(self, cwisystem, dictgen, embeddingsgen, selector, ranker, hard_simps={}, irreplaceable=set([])):
		self.cwisystem = cwisystem
		self.dictgen = dictgen
		self.embeddingsgen = embeddingsgen
		self.selector = selector
		self.ranker = ranker
		self.hard_simps = hard_simps
		self.irreplaceable = irreplaceable

	def getSimplifiability(self, target):
		#Check if there is a CWI system available:
		if self.cwisystem:
			#If so, return the verdict from the CWI system:
			return self.cwisystem.getSimplifiability(target)
		else:
			#If not, assume the word is simplifiable:
			return True

	def generateCandidates(self, sent, target, index, tagged_sents, negatives={}):
		#If target is not irreplaceable:
		if target not in self.irreplaceable and target not in self.hard_simps:
			#Produce candidates based on dictionary map:
			if target not in self.dictgen:
				subs = self.embeddingsgen.getSubstitutionsSingle(sent, target, index, tagged_sents, 10, negatives=negatives)
			else:
				subs = self.embeddingsgen.getSubstitutionsSingle(sent, target, index, tagged_sents, 3, negatives=negatives)
	
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
		else:
			if target in self.irreplaceable:
				return [[sent, target, index]]
			else:
				return [[sent, target, index, '0:'+self.hard_simps[target], '0:'+self.hard_simps[target]]]
	
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
	
	def rankCandidates(self, simpdata, demodata):
		#Rank selected candidates:
		ranks = self.ranker.getRankings(simpdata, demodata)
		return ranks

#Functions:
def getTaggedSentences(sents, configurations, lang):
	tagged_sents = []
	for sent in sents:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect((configurations[lang+'_stanford_tagger_host'], int(configurations[lang+'_stanford_tagger_port'])))
		sinput = sent+'\n' 
		s.send(sinput.encode("utf-8"))
		resp = [token.split(r'_') for token in s.recv(2014).decode('utf-8').strip().split(' ')]
		resp = [(token[0], token[1]) for token in resp]
		tagged_sents.append(resp)
	return tagged_sents

def updateRequest(sent, target, index, tagged):
	#If target is a word:
	if ' ' not in target.strip():
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
	#If target is a phrase:
	else:
		jtarget = target.replace(' ', '_')
		newsent = sent.replace(target, jtarget)
		newindex = 0
		for i, token in enumerate(newsent.split(' ')):
			if token==jtarget:
				newindex = i
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

def getHardSimplifications(file):
	subs = {}
	f = open(file)
	for line in f:
		data = line.strip().split('\t')
		target = data[0].strip()
		cand = data[1].strip()
		subs[target] = cand
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

def getLexicalInteractionData(configurations, token):
	#Create URL request for UPM:
	url = 'http://'+configurations['main_upm_server_host']+':'+configurations['main_upm_server_port']
	url += '/?request_type=request_inter_data&token='+token+'&inter_type=lexical'
	content = urllib2.urlopen(url).read().strip()
	simplifications = json.loads(content)['target'][0]
	bad = {}
	for simp in simplifications:
		target = simp[1].strip()
		if target not in bad:
			bad[target] = set([])
		sub = simp[2].strip()
		feedback = simp[5]
		if feedback==0:
			bad[target].add(sub)
	return simplifications, bad

def getDemographicData(configurations, token):
	#Create URL request for UPM:
	url = 'http://'+configurations['main_upm_server_host']+':'+configurations['main_upm_server_port']
	url += '/?request_type=request_demo_data&token='+token
	content = urllib2.urlopen(url).read().strip()
	demoinfo = json.loads(content)['target'][0]
	demoinfo = formatDemographicDataForRanker(demoinfo)
	return demoinfo

def getSpanishLexicalSimplifier(resources):
	#General purpose:
	victor_corpus = resources['spanish_ubr']
	w2vpm_spa = resources['spa_caretro_embeddings']
	w2vty_spa = resources['spa_typical_embeddings']

	#Generator:
	gg = SIMPATICOGenerator(w2vpm_spa, stemmer=SnowballStemmer('spanish'), tag_class_func=SpanishGetTagClass)

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
	return EnhancedLexicalSimplifier(None, {}, gg, bs, gr)
	
def getEnglishLexicalSimplifier(resources):
	#General purpose:
	victor_corpus = resources['nnseval']
	w2vpm_eng = resources['eng_caretro_embeddings']
	w2vty_eng = resources['eng_typical_embeddings']
	hardsimps_eng = getHardSimplifications(resources['eng_hard_simps'])
	irrep_eng = set([line.strip() for line in open(resources['eng_irreplaceable'])])
	proh_edges = set([line.strip() for line in open(resources['eng_prohibited_phrase_edges'])])
	proh_chars = set([line.strip() for line in open(resources['eng_prohibited_phrase_chars'])])

	#Complex word identifier:
	freq_map = shelve.open(resources['eng_sub_shelf'], protocol=pickle.HIGHEST_PROTOCOL)
	mean_freq = float(resources['eng_mean_freq'])
	std_freq = float(resources['eng_std_freq'])
	min_proportion = float(resources['eng_min_proportion'])
	cwi = EnglishComplexWordIdentifier(freq_map, mean_freq, std_freq, min_proportion)

	#Generator:
	#ng = getNewselaCandidates(resources['newsela_candidates'])
	kg = SIMPATICOGenerator(w2vpm_eng, stemmer=PorterStemmer(), prohibited_edges=proh_edges, prohibited_chars=proh_chars, tag_class_func=EnglishGetTagClass)

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
	filehandler = open(resources['eng_ranker_model'], 'r')
	regmodel = pickle.load(filehandler)
	filehandler.close()
	filehandler = open(resources['eng_ranker_demofarm'], 'r')
	demofarm = pickle.load(filehandler)
	filehandler.close()
	rr = SIMPATICORidgeRegressionRanker(fe, demofarm)
	rr.model = regmodel
#	model_file = resources['nn_sr_model']
#	model = model_from_json(open(model_file+'.json').read())
#	model.load_weights(model_file+'.h5')
#	model.compile(loss='mean_squared_error', optimizer='adam')
#	nr = NNRegressionRanker(fe, model)
	
	#Return LexicalSimplifier object:
	return EnhancedLexicalSimplifier(None, {}, kg, bs, rr, hard_simps=hardsimps_eng, irreplaceable=irrep_eng)
#	return EnhancedLexicalSimplifier(cwi, ng, kg, bs, nr, hard_simps=hardsimps_eng, irreplaceable=irrep_eng)

def getGalicianLexicalSimplifier(resources):
	#General purpose:
	w2vpm_gal = resources['gal_typical_embeddings']
	w2vretro_gal = resources['gal_careretro_embeddings']

	#Generator:
	gg = SIMPATICOGenerator(w2vretro_gal, tag_class_func=GalicianGetTagClass)
	
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
	return EnhancedLexicalSimplifier(None, {}, gg, bs, gr)
	
def getItalianLexicalSimplifier(resources):
	#General purpose:
	w2vpm_ita = resources['ita_typical_embeddings']
	w2vretro_ita = resources['ita_careretro_embeddings']

	#Generator:
	gg = SIMPATICOGenerator(w2vretro_ita, stemmer=SnowballStemmer('italian'), tag_class_func=ItalianGetTagClass)
	
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
	return EnhancedLexicalSimplifier(None, {}, gg, bs, gr)		
	
################################################ MAIN ########################################################	
if __name__ == '__main__':

	#Load global resources and configurations:
	configurations = loadResources('../configurations.txt')
	resources = loadResources('../resources.txt')

	#Load simplifiers:
	simplifier_eng = getEnglishLexicalSimplifier(resources)
#	simplifier_gal = getGalicianLexicalSimplifier(resources)
#	simplifier_ita = getItalianLexicalSimplifier(resources)
#	simplifier_spa = getSpanishLexicalSimplifier(resources)

	#Create simplifier map:
	simplifier_map = {}
	simplifier_map['en'] = simplifier_eng
#	simplifier_map['gl'] = simplifier_gal
#	simplifier_map['it'] = simplifier_ita
#	simplifier_map['es'] = simplifier_spa

	#Wait for simplification requests:
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.bind(('0.0.0.0', int(configurations['ls_local_server_port'])))
	serversocket.listen(5)

	#Upon receival of simplification request, do:
	while 1:
		#Open connection:
		(conn, address) = serversocket.accept()
	
		#Parse request:
		data = None
		try:
			data = conn.recv(1024)
			data = data.decode('utf-8')
			data = json.loads(data)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print 'An error occurred while receiving/parsing a JSON request. Line: ', exc_tb.tb_lineno, ' Message: ', e
			data = None
	
		try:
			token = data['token']
			sent = data['sentence']
			target = data['target']
			index = data['index']
			lang = data['lang']
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print 'An error occurred while checking the integrity of a JSON request. Line: ', exc_tb.tb_lineno, ' Message: ', e
			data = None
			sent = None
			target = None
			index = None
			lang = None

		#Simplify based on language:
		sr_output = [[]]
		try:
			#Tag sentence:
			tagged_sents = getTaggedSentences([sent], configurations, lang)
			#Update request information:
			sent, index = updateRequest(sent, target, int(index), tagged_sents[0])
			#Get lexical interaction data:
			interdata, badsimps = getLexicalInteractionData(configurations, token)
			#Get demographic data:
			demodata = getDemographicData(configurations, token)
			#CWI:
			cwi_output = simplifier_map[lang].getSimplifiability(target)
			if cwi_output:
				#SG:
				sg_output = simplifier_map[lang].generateCandidates(sent, target, index, tagged_sents, negatives=badsimps)
				#SS:
				ss_output = simplifier_map[lang].selectCandidates(sg_output, tagged_sents)
				#SR:
				sr_output = simplifier_map[lang].rankCandidates(ss_output, [demodata])
			else:
				sr_output = [[]]
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print 'An error has ocurred while simplifying the complex word. Line: ', exc_tb.tb_lineno, ' Message: ', e
			sr_output = [[]]

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
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print 'An error has ocurred while sending a response. Line: ', exc_tb.tb_lineno, ' Message: ', e
			conn.send('NULL\n')
			conn.close()
