import unittest
from lib import *
from Run_TCP_Lexical_Simplifier_Server import *

##################################################### REGULAR FUNCTIONS ##############################################

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




















###################################################### UNIT TESTS ####################################################

class TestSimplification(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		#Load self.resources:
		cls.resources = loadResources('../resources.txt')

		#General purpose:
		self.victor_corpus = self.resources['nnseval']
		self.w2vpm_eng = self.resources['eng_caretro_embeddings']
		self.w2vty_eng = self.resources['eng_typical_embeddings']
		self.hardsimps_eng = getHardSimplifications(self.resources['eng_hard_simps'])
		self.irrep_eng = set([line.strip() for line in open(self.resources['eng_irreplaceable'])])
		self.proh_edges = set([line.strip() for line in open(self.resources['eng_prohibited_phrase_edges'])])
		self.proh_chars = set([line.strip() for line in open(self.resources['eng_prohibited_phrase_chars'])])

		#Complex word identifier:
		self.freq_map = shelve.open(self.resources['eng_sub_shelf'], protocol=pickle.HIGHEST_PROTOCOL)
		self.mean_freq = float(self.resources['eng_mean_freq'])
		self.std_freq = float(self.resources['eng_std_freq'])
		self.min_proportion = float(self.resources['eng_min_proportion'])
		self.cwi = EnglishComplexWordIdentifier(self.freq_map, self.mean_freq, self.std_freq, self.min_proportion)

		#Generator:
		self.ng = getNewselaCandidates(self.resources['newsela_candidates'])
		self.kg = SIMPATICOGenerator(self.w2vpm_eng, stemmer=PorterStemmer(), prohibited_edges=self.proh_edges, prohibited_chars=self.proh_chars, tag_class_func=EnglishGetTagClass)
			
		#Selector:
		fe = FeatureEstimator()
		fe.addCollocationalFeature(self.resources['eng_sub_lm'], 2, 2, 'Complexity')
		fe.addWordVectorSimilarityFeature(self.w2vty_eng, 'Simplicity')
		self.br = BoundaryRanker(fe)
		self.bs = BoundarySelector(self.br)
		self.bs.trainSelectorWithCrossValidation(self.victor_corpus, 2, 5, 0.25, k='all')

		#Ranker:
		fe = FeatureEstimator(norm=False)
		fe.addCollocationalFeature(self.resources['eng_sub_lm'], 2, 2, 'Simplicity')
		self.model_file = self.resources['nn_sr_model']
		self.model = model_from_json(open(self.model_file+'.json').read())
		self.model.load_weights(self.model_file+'.h5')
		self.model.compile(loss='mean_squared_error', optimizer='adam')
		self.nr = NNRegressionRanker(fe, self.model)

		#Return LexicalSimplifier object:
		self.eng_simplifier = EnhancedLexicalSimplifier(self.cwi, self.ng, self.kg, self.bs, self.nr, hard_simps=self.hardsimps_eng, irreplaceable=self.irrep_eng)

	def test_complex_word_cwi(self):
		self.assertTrue(self.cwi.getSimplifiability('refreshments'))

	def test_simple_word_cwi(self):
		self.assertFalse(self.cwi.getSimplifiability('chair'))

	def test_oov_word_cwi(self):
		self.assertFalse(self.cwi.getSimplifiability('afakeword'))

	def test_in_vocab_word_embedsg(self):
		sentence = 'but they reflect the gallantry .'
		target = 'gallantry'
		index = '4'
		tagged_sents = [[('but', 'CC'), ('they', 'PP'), ('reflect', 'V'), ('the', 'DT'), ('gallantry', 'N'), ('.', '.')]]
		amount = 10
		generated = self.kg.getSubstitutionsSingle(sentence, target, index, tagged_sents, amount)
		self.assertTrue(len(generated[target])==10)

	def test_oov_word_embedsg(self):
		sentence = 'but they reflect the afakeword .'
		target = 'afakeword'
		index = '4'
		tagged_sents = [[('but', 'CC'), ('they', 'PP'), ('reflect', 'V'), ('the', 'DT'), ('afakeword', 'N'), ('.', '.')]]
		amount = 10
		result = self.kg.getSubstitutionsSingle(sentence, target, index, tagged_sents, amount)
		self.assertTrue(len(result[target])==0)

	def test_in_vocab_phrase_embedsg(self):
		sentence = 'mercury is a chemical_substance that is toxic'
		target = 'chemical_substance'
		index = '3'
		tagged_sents = [[('mercury', 'CC'), ('is', 'PP'), ('a', 'V'), ('chemical', 'DT'), ('substance', 'N'), ('that', '.'), ('is', '.'), ('toxic', '.')]]
		amount = 10
		result = self.kg.getSubstitutionsSingle(sentence, target, index, tagged_sents, amount)
		self.assertTrue(len(result[target])==10)

	def test_oov_phrase_embedsg(self):
		sentence = 'mercury is a chemical_substance that is toxic'
		target = 'fake_phrase'
		index = '3'
		tagged_sents = [[('mercury', 'CC'), ('is', 'PP'), ('a', 'V'), ('chemical', 'DT'), ('substance', 'N'), ('that', '.'), ('is', '.'), ('toxic', '.')]]
		amount = 10
		result = self.kg.getSubstitutionsSingle(sentence, target, index, tagged_sents, amount)
		self.assertTrue(len(result[target])==0)	

	def test_word_boundss(self):
		sentence = 'but they reflect the gallantry .'
		target = 'gallantry'
		index = '4'
		cands = ['bravery', 'courage', 'valour', 'pluck']
		data = [sentence, target, index]
		data.extend(['0:'+cand for cand in cands])
		data = [data]
		selected = self.bs.selectCandidates(data, 0.5, proportion_type='percentage')
		self.assertTrue(len(selected[0])==2)
		
	def test_phrase_boundss(self):
		sentence = 'mercury is a chemical_substance that is toxic'
		target = 'chemical_substance'
		index = '3'
		cands = ['chemical', 'substance', 'compound', 'component']
		data = [sentence, target, index]
		data.extend(['0:'+cand for cand in cands])
		data = [data]
		selected = self.bs.selectCandidates(data, 0.5, proportion_type='percentage')
		self.assertTrue(len(selected[0])==2)








####################################################### RUN UNIT TESTS ################################################

if __name__ == '__main__':
	#Run all unit tests:
	unittest.main()
