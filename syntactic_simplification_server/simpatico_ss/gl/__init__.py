#!/usr/bin/python
# -*- coding: latin-1 -*-

import os

path = os.path.join(os.path.dirname(__file__), "dicc.src.verbs")

f = open(path, "r")

verbs = {}
lemmas = {}

for s in f.readlines():
    tokens = s.strip().split(" ")
    v = tokens[0]
    l = len(tokens)
    verbs[v] = {}
    for i in range(1,l):
        if (i % 2 == 0):
            verbs[v][tokens[i]] = tokens[i-1]

f.close()

path = os.path.join(os.path.dirname(__file__), "dicc.src.lemmas")

f = open(path, "r")

for s in f.readlines():
    tokens = s.strip().split("\t")
    l = tokens[0].strip()
    lemmas[l] = {}
    for i in range(1,len(tokens)):
        tokens2 = tokens[i].split(":")
        lemmas[l][tokens2[0]] = tokens2[1]


def verb_infinitive(verb, tag):
    try:
        return verbs[verb][tag].encode("utf-8")
    except:
        return ""

def verb_conjugate(verb, tag, tag2):
    try:
        inf = verbs[verb][tag]
        return lemmas[inf][tag2].encode("utf-8")
    except:
        return ""

#print verb_infinitive("metido", "VMP00SM")
#print verb_conjugate("metido", "VMP00SM", "VSIS3S0")


#print
#print "VSIS3S0"
