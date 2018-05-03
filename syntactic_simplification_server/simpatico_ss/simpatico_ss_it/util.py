#!/usr/bin/python
# -*- coding: latin-1 -*-

from nltk.parse.stanford import StanfordDependencyParser
from corenlp import StanfordCoreNLP
import time

class Parser():
    def __init__(self, corenlp_dir, properties):
        #corenlp_dir = "/export/data/ghpaetzold/simpatico/server_simplifiers/core_nlp/stanford-corenlp-full-2016-10-31/"
        #corenlp_dir = "/export/data/cscarton/simpatico/stanford-corenlp-full-2016-10-31/"
        self.corenlp = StanfordCoreNLP(corenlp_dir, memory="4g", properties=properties)
    
    def process(self, sentence):
        #sentences = open(self.doc, "r").read().strip().split("\n")
        #sentences = [l.strip().split(' ') for l in f_read]
        #dep_parser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
        return self.corenlp.raw_parse(sentence)['sentences'][0]

    def transform(self, parsed):
        dict_dep = {}
        for rel, _, head, word, n in parsed['dependencies']:
            
            n = int(n)
            head = int(head)

            if head not in dict_dep.keys():
                dict_dep[head] = {}
            if rel not in dict_dep[head].keys():
                dict_dep[head][rel] = []

            dict_dep[head][rel].append(n)
                


        return dict_dep
