from lib import *
from lexenstein.morphadorner import *
from lexenstein.spelling import *
from lexenstein.features import *
import socket

#Functions:
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

	#Get subs:
	subs, tagged_sents = kg.getSubstitutionsSingle(sent, target, index, 3)
	fulldata = [sent, target, index]
	for sub in subs[target]:
		fulldata.append('0:'+sub)
	if target in newselasubs:
		for sub in newselasubs[target]:
			fulldata.append('0:'+sub)
	fulldata = [fulldata]

	#Select them:
	bs.ranker.fe.temp_resources['tagged_sents'] = tagged_sents
	if len(subs[target])==0:
		selected = [[]]
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
