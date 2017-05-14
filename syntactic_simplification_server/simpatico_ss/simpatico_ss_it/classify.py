import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.externals import joblib
import sys
import string


class Classify:


    def extract_features(self, dict_dep, sentence, words):
        features = []

        markers = ("quando", "dopo", "altrimenti", "pero", "quindi", "mentre", "se", "o", "e", "che", "quale", "prima", "comunque", "cui", "chi")

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
            if pos[0] == "V":
                verb += 1.
            elif pos[0] == "N":
                noun += 1.
            elif pos[0] == "A":
                adj += 1.
            elif pos[0] == "B":
                adv += 1.

            if pos not in string.punctuation:
                tokens += 1.
            else:
                punct += 1.

            if w[0] in markers:
                mark += 1.

        cw = verb + noun + adj + adv

        if cw == 0.:
            cw = 1.

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

    
    def classify(self, sent, dict_dep, words):
        features = np.array(self.extract_features(dict_dep, sent, words))
        features = features.reshape(1,-1) 
        clf = joblib.load('../../data/complex_classifier/it/model.pkl')
        pred = clf.predict(features)

        return pred

    

