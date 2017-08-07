#!/usr/bin/python
# -*- coding: latin-1 -*-
import os

path = os.path.join(os.path.dirname(__file__), "dicc.src.verbs")

f = open(path, "r")

verbs = {}
verbsT = {}
lemmas = {}
adjInf = {}

for s in f.readlines():
    tokens = s.strip().split(" ")
    v = tokens[0]
    l = len(tokens)
    verbs[v] = {}
    verbsT[v] = {}
    for i in range(1,l):
        if (i % 2 == 0):
            verbs[v][tokens[i].lower()] = tokens[i-1] 
            verbsT[v][tokens[i][:4].lower()] = tokens[i-1]

f.close()

path = os.path.join(os.path.dirname(__file__), "dicc.src.lemmas")

f = open(path, "r")

for s in f.readlines():
    tokens = s.strip().split("\t")
    l = tokens[0].strip()
    lemmas[l] = {}
    for i in range(1,len(tokens)):
        tokens2 = tokens[i].split(":")
        lemmas[l][tokens2[1]] = tokens2[0]
        

path = os.path.join(os.path.dirname(__file__), "dicc.src.adj2inf")
f = open(path, "r")
for s in f.readlines():
    tokens = s.strip().split("\t")
    l = tokens[0].strip()
    adjInf[l] = tokens[1].strip()


def verb_infinitive(verb, tag):
    try:
        return verbs[verb][tag[:4]]
    except:
        return ""

def verb_conjugate(verb, tag, tag2=None):
    try:
        if tag2 != None:
            inf = verbs[verb][tag[:4]]
            return lemmas[inf][tag2]
        else:
            return lemmas[verb][tag]  
    except:
        return ""
    
def verb_conjugate_ADDPersonNumber(verb, vtag, article=None, aux_verb=None):
    try:
        if aux_verb != None:
            if "aq" in vtag or verb not in verbsT: 
            
                if verb[-1] == "s":
                    verb = verb[:-1]
                if verb[-3:] in ["ado","ada"]:
                    inf = verb[:-3]+"ar"
                elif verb[-3:] not in ["ido","ida"]: #irregular past participle
                    inf = adjInf[verb]
                elif verb[-3:] in ["ido","ida"]:
                    if verb[:-3]+"er" in verbsT.keys():
                        inf = verb[:-3]+"er"
                    if verb[:-3]+"ir" in verbsT.keys():
                        inf = verb[:-3]+"ir"
                vtag="vmp0000" 
                            
            else:
                inf = verbsT[verb][vtag[:4]]
            newtag  = ""
            newtag  = vtag[0:2] #
            
            aux_tag = ""

            for tag in verbs[aux_verb]:
                if "v" == tag[0]: 
                    aux_tag = tag 
            
            newtag += aux_tag[2:5]  #
                        
            if article in ["los","las","unos","unas"]:
                newtag += "p0"
            else:
                newtag += "s0"


            return lemmas[inf][newtag]
        else:
            return lemmas[verb][vtag]
    except:
        print "except:",verb, vtag, article, aux_verb
        return ""


#print verb_conjugate_ADDPersonNumber("contados", "vmp0000", "el",  "son")
#print verb_infinitive("abandona", "vmip000")
#print verb_conjugate("abandona", "vmip000", "vmip0000")


