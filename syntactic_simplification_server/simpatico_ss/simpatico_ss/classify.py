import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.externals import joblib
import sys
import string

class Classify:


    def extract_features(self, dict_dep, sentence, words):
        features = []

        markers = ("when", "after", "since", "before", "once", "although", "though", "but", "however", "whereas", "because", "so", "while", "if", "or", "and", "whom", "whose", "which", "who", "by")

        ## basic counts
        verb = 0.
        noun = 0.
        adj = 0.
        adv = 0.
        tokens = 0.
        punct = 0.
        mark = 0.
        for w in words:
            pos = w[1]["PartOfSpeech"]
            if pos in ("VB", "VBD", "VBG", "VBN", "VBP", "VBZ"):
                verb += 1.
            elif pos in ("NN", "NNS", "NNP", "NNPS"):
                noun += 1.
            elif pos in ("JJ", "JJS", "JJR"):
                adj += 1.
            elif pos in ("RB", "RBS", "RBR"):
                adv += 1.

            if pos not in string.punctuation:
                tokens += 1.
            else:
                punct += 1.

            if w[0] in markers:
                mark += 1.

        cw = verb + noun + adj + adv

        verb_inc = verb/cw
        noun_inc = noun/cw
        adj_inc = adj/cw
        adv_inc = adv/cw

        mark_inc = mark/tokens

        features.append(tokens)
        features.append(punct)
        features.append(cw)
        features.append(verb_inc)
        features.append(noun_inc)
        features.append(adj_inc)
        features.append(adv_inc)
        features.append(mark_inc)

        ## clauses
        clause = 0.
        if 0 in dict_dep:
            if 'root' in dict_dep[0]:
                root = dict_dep[0]['root'][0]
                if root in dict_dep:
                    dep_root = dict_dep[root]
        
                    for k in dep_root.keys():
                        if k in ("acl", "acl:relcl", "advcl", "conj", "cc"):
                            clause += 1.

        features.append(clause)


        return features

    
    def classify(self, sent, dict_dep, words, comp_model):
        features = np.array(self.extract_features(dict_dep, sent, words))
        features = features.reshape(1,-1) 
        clf = joblib.load(comp_model)
        pred = clf.predict(features)

        return pred

    

