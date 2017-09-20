#!/usr/bin/python
# -*- coding: latin-1 -*-

from nltk.parse.stanford import StanfordDependencyParser
from corenlp import StanfordCoreNLP


import time

class Parser():
    def __init__(self, corenlp_dir, properties):
        self.corenlp = StanfordCoreNLP(corenlp_dir, memory="4g", properties=properties)
    
    def process(self, sentence):
        parse=self.corenlp.raw_parse(sentence)
        if parse['sentences'] == []:  
            parse=self.corenlp.raw_parse(sentence)
        return parse['sentences'][0]

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
