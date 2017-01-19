from lib import *
from lexenstein.morphadorner import *
from lexenstein.spelling import *
from lexenstein.features import *
import socket

#Functions:
def getTaggedSentences(sents):
                tagged_sents = []
                for sent in sents:
                        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        s.connect(("localhost",2020))
                        s.send(sent+'\n')
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

#General purpose:
m = MorphAdornerToolkit('/export/data/ghpaetzold/LEXenstein/morph/')
nc = NorvigCorrector('/export/data/ghpaetzold/LEXenstein/corpora/norvig_model_wmt.bin', format='bin')
victor_corpus = '/export/data/ghpaetzold/benchmarking/paetzold_nns/corpora/paetzold_nns_dataset.txt'
pos_model = '/export/data/ghpaetzold/benchmarking/lexmturk/scripts/evaluators/stanford-postagger-full-2015-04-20/models/wsj-0-18-left3words-distsim.tagger'
stanford_tagger = '/export/data/ghpaetzold/benchmarking/lexmturk/scripts/evaluators/stanford-postagger-full-2015-04-20/stanford-postagger.jar'
w2vpm = '/export/data/ghpaetzold/word2vecvectors/models/word_vectors_all_generalized_1300_cbow_retrofitted.bin'

#Generator:
newselasubs = getNewselaCandidates('/export/data/ghpaetzold/benchmarking/lseval+lexmturk/substitutions/newsela/substitutions.txt')
kg = PaetzoldGenerator(w2vpm, nc, pos_model, stanford_tagger, '/usr/bin/java')

#Selector:
fe = FeatureEstimator()
fe.addCollocationalFeature('/export/data/ghpaetzold/subtitlesimdb/corpora/160715/subtleximdb.5gram.unk.bin.txt', 2, 2, 'Complexity')
fe.addTargetPOSTagProbability('/export/data/ghpaetzold/LEXenstein/corpora/POS_condprob_model.bin', pos_model, stanford_tagger, '/usr/bin/java', 'Simplicity')
fe.addTaggedWordVectorSimilarityFeature(w2vpm, pos_model, stanford_tagger, '/usr/bin/java', 'paetzold', 'Simplicity')
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

	#Tag sentence:
	tagged_sents = getTaggedSentences([sent])

	#Update request information:
	sent, index = updateRequest(sent, target, int(index), tagged_sents[0])

	print (sent, target, index)

	#Get subs:
	if target not in newselasubs:
		subs = kg.getSubstitutionsSingle(sent, target, index, tagged_sents, 10)
	else:
		subs = kg.getSubstitutionsSingle(sent, target, index, tagged_sents, 3)

	#Create input data instance:
	fulldata = [sent, target, index]
	for sub in subs[target]:
		fulldata.append('0:'+sub)
	if target in newselasubs:
		for sub in newselasubs[target]:
			fulldata.append('0:'+sub)
	fulldata = [fulldata]

	#Select them:
	bs.ranker.fe.temp_resources['tagged_sents'] = tagged_sents
	if len(fulldata[0])<5:
		selected = [[]]
		print 'Entered here!'
	else:
		selected = bs.selectCandidates(subs, fulldata, 0.5, proportion_type='percentage')		

	#Rank them:
	fulldata = [sent, target, index]
        for sub in selected[0]:
                fulldata.append('0:'+sub)
        fulldata = [fulldata]
	ranks = nr.getRankings(fulldata)

	#Get final replacement:
	replacement = 'NULL'
	if len(ranks[0])>0:
		replacement = ranks[0][0]	

	#Send result:
	conn.send(replacement+'\n')
	conn.close()
