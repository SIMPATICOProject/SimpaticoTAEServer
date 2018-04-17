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
		#Load cls.resources:
		cls.resources = loadResources('../resources.txt')

		#General purpose:
		cls.victor_corpus = cls.resources['nnseval']
		cls.w2vpm_eng = cls.resources['eng_caretro_embeddings']
		cls.w2vty_eng = cls.resources['eng_typical_embeddings']
		cls.hardsimps_eng = getHardSimplifications(cls.resources['eng_hard_simps'])
		cls.irrep_eng = set([line.strip() for line in open(cls.resources['eng_irreplaceable'])])
		cls.proh_edges = set([line.strip() for line in open(cls.resources['eng_prohibited_phrase_edges'])])
		cls.proh_chars = set([line.strip() for line in open(cls.resources['eng_prohibited_phrase_chars'])])

		#Complex word identifier:
		cls.freq_map = shelve.open(cls.resources['eng_sub_shelf'], protocol=pickle.HIGHEST_PROTOCOL)
		cls.mean_freq = float(cls.resources['eng_mean_freq'])
		cls.std_freq = float(cls.resources['eng_std_freq'])
		cls.min_proportion = float(cls.resources['eng_min_proportion'])
		cls.cwi = EnglishComplexWordIdentifier(cls.freq_map, cls.mean_freq, cls.std_freq, cls.min_proportion)

		#Generator:
		cls.ng = getNewselaCandidates(cls.resources['newsela_candidates'])
		cls.kg = SIMPATICOGenerator(cls.w2vpm_eng, stemmer=PorterStemmer(), prohibited_edges=cls.proh_edges, prohibited_chars=cls.proh_chars, tag_class_func=EnglishGetTagClass)
			
		#Selector:
		fe = FeatureEstimator()
		fe.addCollocationalFeature(cls.resources['eng_sub_lm'], 2, 2, 'Complexity')
		fe.addWordVectorSimilarityFeature(cls.w2vty_eng, 'Simplicity')
		cls.br = BoundaryRanker(fe)
		cls.bs = BoundarySelector(cls.br)
		cls.bs.trainSelectorWithCrossValidation(cls.victor_corpus, 2, 5, 0.25, k='all')

		#Ranker:
		fe = FeatureEstimator(norm=False)
		fe.addCollocationalFeature(cls.resources['eng_sub_lm'], 2, 2, 'Simplicity')
		cls.model_file = cls.resources['nn_sr_model']
		cls.model = model_from_json(open(cls.model_file+'.json').read())
		cls.model.load_weights(cls.model_file+'.h5')
		cls.model.compile(loss='mean_squared_error', optimizer='adam')
		cls.nr = NNRegressionRanker(fe, cls.model)

		#Return LexicalSimplifier object:
		cls.eng_simplifier = EnhancedLexicalSimplifier(cls.cwi, cls.ng, cls.kg, cls.bs, cls.nr, hard_simps=cls.hardsimps_eng, irreplaceable=cls.irrep_eng)

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
		target = 'chemical substance'
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
