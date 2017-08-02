import os
import sys
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.dummy import DummyClassifier
from sklearn.cross_validation import KFold
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score, recall_score
from textstat.textstat import textstat
from sklearn.grid_search import GridSearchCV
import string
import pickle
from sklearn.externals import joblib
import kenlm
import grammar_check

sys.path[0:0] = ["../simpatico_ss"]
from simpatico_ss.util import Parser

class Train:

    def extract_features(self, dict_dep, sentence, words, model, tool):
        features = []

        logprob = model.score(sentence)
        perplexity = model.perplexity(sentence)

        features.append(logprob)
        features.append(perplexity)

        matches = tool.check(unicode(sentence, errors='ignore'))

        errors = 0.
        for m in matches:
            if m.category != 'Miscellaneous':
                errors += 1.

        features.append(errors)


        ## basic counts
        verb = 0.
        noun = 0.
        adj = 0.
        adv = 0.
        tokens = 0.
        punct = 0.
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

        cw = verb + noun + adj + adv

        verb_inc = verb/cw
        noun_inc = noun/cw
        adj_inc = adj/cw
        adv_inc = adv/cw

        features.append(tokens)
        features.append(punct)
        features.append(cw)
        features.append(verb_inc)
        features.append(noun_inc)
        features.append(adj_inc)
        features.append(adv_inc)

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
        #clf = GaussianNB()
        clf = RandomForestClassifier()
        #clf = SVC()
        clf.fit(features, labels)
        joblib.dump(clf, 'model.pkl')

        svr_parameters = {'C':[1, 10,2], 'gamma':[0.0001, 0.01, 2]}
        
        kf = KFold(len(features), n_folds=10)

        f1 = 0.
        acc = 0.
        precision = 0.
        recall = 0.

        f1_dummy = 0.
        acc_dummy = 0.
        p_dummy = 0.
        r_dummy = 0.
        for train, test in kf:
            clf = RandomForestClassifier()
            clf_dummy = DummyClassifier()
            #clf = GaussianNB()
            #clf = GridSearchCV(SVC(), svr_parameters, cv = 5)
            clf.fit(features[train],labels[train])
            clf_dummy.fit(features[train],labels[train])
            pred = clf.predict(features[test])
            pred_dummy = clf_dummy.predict(features[test])
            f1 += f1_score(labels[test], pred)
            acc += accuracy_score(labels[test], pred)
            precision += precision_score(labels[test], pred)
            recall += recall_score(labels[test], pred)

            f1_dummy += f1_score(labels[test], pred_dummy)
            acc_dummy += accuracy_score(labels[test], pred_dummy)
            p_dummy += precision_score(labels[test], pred_dummy)
            r_dummy += recall_score(labels[test], pred_dummy)

        final_p = precision/10.
        final_r = recall/10.
        f1 = 2*(final_p*final_r)/(final_p+final_r)
        final_p_dummy = p_dummy/10.
        final_r_dummy = r_dummy/10.
        f1_dummy = 2*(final_p_dummy*final_r_dummy)/(final_p_dummy+final_r_dummy)
        
        return f1, acc/10., final_p, final_r, f1_dummy, acc_dummy/10., final_p_dummy, final_r_dummy



class __main__:

    def parser_server():
        stfd_parser = Parser("../../data/stanford-corenlp-full-2016-10-31", "../../data/english.myproperties.properties")
        return stfd_parser
    
    f = open(sys.argv[1], "r")
    #labels = np.loadtxt(sys.argv[2]
    labels = []

    stfd_parser = parser_server()
    train = Train()

    model = kenlm.Model('/export/data/cscarton/corpora/training_full.blm.en')

    tool = grammar_check.LanguageTool('en-GB')
    
    feat_file = open("tmp.features", "w")
    c_0 = 0
    c_1 = 0

    for s in f.readlines():

        t = s.split("\t")

        src = t[0].strip()
        tgt = t[2].strip()

        l = int(t[3].strip())
        if l == 4:
            labels.append(1)
            c_0+=1
        else:
            labels.append(0)
            c_1+=1

        parsed = stfd_parser.process(src)
    
        ## data structure for the words and POS
        words = parsed['words']
    
        #print words

        ## data structure for the dependency parser
        dict_dep = stfd_parser.transform(parsed)

        #print dict_dep

        features_src = train.extract_features(dict_dep, src, words, model, tool)

        parsed = stfd_parser.process(tgt)


        ## data structure for the words and POS
        words = parsed['words']
    
        #print words

        ## data structure for the dependency parser
        dict_dep = stfd_parser.transform(parsed)

        #print dict_dep

        features_tgt = train.extract_features(dict_dep, tgt, words, model, tool)

        
        for feature in features_src:
            feat_file.write(str(feature))
            feat_file.write("\t")
        for feature in features_tgt:
            feat_file.write(str(feature))
            feat_file.write("\t")
        feat_file.write("\n")

    feat_file.close()

    feat_read = np.loadtxt("tmp.features")

    print c_0, c_1

    print train.train(feat_read, np.array(labels))


