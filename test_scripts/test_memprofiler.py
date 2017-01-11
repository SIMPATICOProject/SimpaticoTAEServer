import gensim

path = '/export/data/ghpaetzold/word2vecvectors/models/word_vectors_all_generalized_1300_cbow_retrofitted.bin'

m = gensim.models.word2vec.Word2Vec.load_word2vec_format(path, binary=True)
print 'Loaded'
while 1:
	pass
