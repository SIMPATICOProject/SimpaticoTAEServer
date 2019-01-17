from nltk.corpus import wordnet as wn
import sys

target = sys.argv[1]
syns = wn.synsets(target)

for syn in syns:
	lemmas = syn.lemmas()
	synonyms = [w.name().replace('_', ' ') for w in lemmas]
	print synonyms

print wn.ADV
print wn.VERB
print wn.NOUN
print wn.ADJ
