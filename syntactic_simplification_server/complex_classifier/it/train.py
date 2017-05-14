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
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score, recall_score
from textstat.textstat import textstat
import string
import pickle
from sklearn.externals import joblib
import string

sys.path[0:0] = ["../../simpatico_ss"]
from simpatico_ss_it.util import Parser
from simpatico_ss_it.classify import Classify

class Train:


    def train(self, features, labels):
        clf = GaussianNB()
        #clf = RandomForestClassifier()
        #clf = SVC()
        clf.fit(features, labels)
        joblib.dump(clf, 'model.pkl')
        
        kf = KFold(len(features), n_folds=10)

        f1 = 0.
        f1_dummy = 0.
        acc = 0.
        acc_dummy = 0.
        precision = 0.
        p_dummy = 0.
        recall = 0.
        r_dummy = 0.
        for train, test in kf:
            clf = GaussianNB()
            clf_dummy = DummyClassifier(strategy='most_frequent')
            #clf = SVC(gamma=2, C=1)
            clf.fit(features[train],labels[train])
            clf_dummy.fit(features[train],labels[train])
            pred = clf.predict(features[test])
            pred_dummy = clf_dummy.predict(features[test])
            f1 += f1_score(labels[test], pred)
            f1_dummy += f1_score(labels[test], pred_dummy)
            acc += accuracy_score(labels[test], pred)
            acc_dummy += accuracy_score(labels[test], pred_dummy)
            precision += precision_score(labels[test], pred)
            p_dummy += precision_score(labels[test], pred_dummy)
            recall += recall_score(labels[test], pred)
            r_dummy += recall_score(labels[test], pred_dummy)

        return f1/10., acc/10., precision/10., recall/10., f1_dummy/10., acc_dummy/10., p_dummy/10., r_dummy/10.


class __main__:

    def parser_server():
        stfd_parser = Parser("../../../data/stanford-corenlp-full-2016-10-31", "../../../data/italian.myproperties.properties")
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


        features = Classify().extract_features(dict_dep, s, words)
        
        for feature in features:
            feat_file.write(str(feature))
            feat_file.write("\t")
        feat_file.write("\n")

    feat_file.close()

    feat_read = np.loadtxt("tmp.features")

    print train.train(feat_read, labels)
