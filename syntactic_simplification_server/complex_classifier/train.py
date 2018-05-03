import os
import sys
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cross_validation import KFold
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score, recall_score
from textstat.textstat import textstat
import string
import pickle
from sklearn.externals import joblib

sys.path[0:0] = ["../simpatico_ss"]
from simpatico_ss.util import Parser

class Train:

    def extract_features(self, dict_dep, sentence, words):
        features = []

        markers = ("when", "after", "since", "before", "once", "although", "though", "but", "however", "whereas", "because", "so", "while", "if", "or", "and", "whom", "whose", "which", "who", "by")

        ## flesch
        #try:
        #    flesch = textstat.flesch_reading_ease(sentence)
        #except:
        #    flesch = 0.

        #features.append(flesch)


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

    def train(self, features, labels):
        clf = GaussianNB()
        #clf = RandomForestClassifier()
        #clf = SVC()
        clf.fit(features, labels)
        joblib.dump(clf, 'model.pkl')
        
        kf = KFold(len(features), n_folds=10)

        f1 = 0.
        acc = 0.
        precision = 0.
        recall = 0.
        for train, test in kf:
            clf = GaussianNB()
            #clf = SVC(gamma=2, C=1)
            clf.fit(features[train],labels[train])
            pred = clf.predict(features[test])
            f1 += f1_score(labels[test], pred)
            acc += accuracy_score(labels[test], pred)
            precision += precision_score(labels[test], pred)
            recall += recall_score(labels[test], pred)

        return f1/10., acc/10., precision/10., recall/10.



class __main__:

    def parser_server():
        stfd_parser = Parser("../../data/stanford-corenlp-full-2016-10-31", "../../data/english.myproperties.properties")
        return stfd_parser
    
    f = open(sys.argv[1], "r")
    labels = np.loadtxt(sys.argv[2])

    stfd_parser = parser_server()

    train = Train()
    
    feat_file = open("tmp.features", "w")

    for s in f.readlines():

        parsed = stfd_parser.process(s)
    
        ## data structure for the words and POS
        words = parsed['words']
    
        #print words

        ## data structure for the dependency parser
        dict_dep = stfd_parser.transform(parsed)

        #print dict_dep

        features = train.extract_features(dict_dep, s, words)
        
        for feature in features:
            feat_file.write(str(feature))
            feat_file.write("\t")
        feat_file.write("\n")

    feat_file.close()

    feat_read = np.loadtxt("tmp.features")

    print train.train(feat_read, labels)
