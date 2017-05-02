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
            verbs[v][tokens[i][:4].lower()] = tokens[i-1]

f.close()

path = os.path.join(os.path.dirname(__file__), "dicc.src.lemmas")

f = open(path, "r")

for s in f.readlines():
    tokens = s.strip().split("\t")
    l = tokens[0].strip()
    lemmas[l] = {}
    for i in range(1,len(tokens)):
        tokens2 = tokens[i].split(":")
        lemmas[l][tokens2[1][:4]] = tokens2[0]

def verb_infinitive(verb, tag):
    try:
        return verbs[verb][tag[:4]]
    except:
        return ""

def verb_conjugate(verb, tag, tag2=None):
    try:
        if tag2 != None:
            inf = verbs[verb][tag[:4]]
            return lemmas[inf][tag2[:4]]
        else:
            return lemmas[verb][tag2[:4]]
    except:
        return ""


#print verb_infinitive("abandona", "vmip000")
#print verb_conjugate("abandona", "vmip000", "vmip0000")


#print
#print "VSIS3S0"
