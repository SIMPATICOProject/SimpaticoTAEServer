#!/usr/bin/python
# -*- coding: latin-1 -*-

import es
from truecaser.Truecaser import *
import cPickle

class Generation:

    def __init__(self, time, concession, justify, condition, condition2, addition, cc, relpron, truecase_model):
        """
        Perform the regeneration of simplified sentences.
        @param time: list of temporal markers
        @param concession: list of concession markers
        @param justify: list of justification markers
        @param condition: list of conditional markers (if)
        @param condition2: list of conditional markers (either..or)
        @param addition: list of addition markers
        @param cc: list of all markers
        @param relpron: list of relative pronouns
        @param truecase_model: truecase model
        """

        self.time = time
        self.concession = concession
        self.justify = justify
        self.condition = condition
        self.condition2 = condition2
        self.addition = addition
        self.cc = cc
        self.relpron = relpron

        f = open(truecase_model, 'rb')
        self.uniDist = cPickle.load(f)
        self.backwardBiDist = cPickle.load(f)
        self.forwardBiDist = cPickle.load(f)
        self.trigramDist = cPickle.load(f)
        self.wordCasingLookup = cPickle.load(f)
        f.close()

    def runTrueCaser(self, sentence):
        """
        Perform truecasing (use the truecaser from https://github.com/nreimers/truecaser)
        @param sentence: sentence to be truecased
        @return: truecased sentence
        """
        tokensCorrect = sentence.split(" ")
        tokens = [token.lower() for token in tokensCorrect]
        tokensTrueCase = getTrueCase(tokens, 'title', self.wordCasingLookup, self.uniDist, self.backwardBiDist, self.forwardBiDist, self.trigramDist)
        
        perfectMatch = True
        
        for idx in xrange(len(tokensCorrect)):
            if not tokensCorrect[idx] == tokensTrueCase[idx]:
                perfectMatch = False
        
        if not perfectMatch:
            #tokensCorrect
            return " ".join(tokensTrueCase)

        else:
            return sentence


    def print_sentence(self, final1, final2, root_tag=None, mark=None, mark_pos=None, modal=None):
        """
        Finalise the simplification process by including markers and punctuation.
        @param final1: dictionary of first clause 
        @param final2: dictionary of second clause
        @param root_tag: POS tag of the root node
        @param mark: marker that triggered the simplification
        @param mark_pos: position of the marker that triggered the simplification
        @param modal: modal verb (if any)
        @return: two sentences, one for each clause.
        """ 
        s_sentence = ''
        s_sentence2 = ''
        
        ## control the markers that should be added into the simplified sentences
        if mark in self.addition:
            s_sentence2 += 'Y '
        if mark in self.condition:
            s_sentence += 'Supponiamo '
            # s_sentence2 += 'Entonces '
        elif mark in self.concession:
            s_sentence2 += 'Ma '

        ## English implementation -->  need to be adapted to Spanish    
        #elif mark in self.time:
        #    if mark_pos > 1:
        #        if root_tag == 'VBP' or root_tag == 'VBZ' or root_tag == 'VB':
        #            s_sentence2 += 'This is ' + mark + " "
        #        else:
        #            s_sentence2 += 'This was ' + mark + " "
        #    else:

        #        if root_tag == 'VBP' or root_tag == 'VBZ':
        #            s_sentence2 += 'This happens ' + mark + " "
        #        elif root_tag == 'VB' and modal != None: 
        #            s_sentence2 += 'This ' + modal + ' happen ' + mark + " "
        #        else:
        #            s_sentence2 += 'This happened ' + mark + " "

        elif mark in self.justify:
            s_sentence2 += 'Quindi '
        elif mark in self.condition2:
            s_sentence2 += 'Alternativamente '
        
        c = 0

        ## build first sentence
        for k in sorted(final1.keys()):
            if c == 0 and final1[k] in (".", ",", "?", ":", ";", "!"):
                c+=1
            else:
                s_sentence += final1[k] + " "
                c+=1

        c = 0
        ## build second sentence
        for k in sorted(final2.keys()):
            if c ==0 and final2[k] in (".", ",", "?", ":", ";", "!"):
                c+=1
            else:
                s_sentence2 += final2[k] + " "
                c+=1
        

        s_sentence = s_sentence[0].capitalize() + s_sentence[1:]
        s_sentence2 = s_sentence2[0].capitalize() + s_sentence2[1:]
       
        #including final punctuation
        if final1[sorted(final1.keys())[-1]] not in (".", "?", "!"):
            s_sentence+= ". "

        if final2[sorted(final2.keys())[-1]] not in (".", "?", "!"):
            s_sentence2+= ". "

       
        #removing errors in punctuation
        s_sentence = s_sentence.replace(", .", ".").replace("; .", ".").replace(": .", ".").replace(", ?", "?").replace("; ?", "?").replace(": ?", "?").replace(", !", "!").replace("; !", "!").replace(": !", "!")
        s_sentence2 = s_sentence2.replace(", .", ".").replace("; .", ".").replace(": .", ".").replace(", ?", "?").replace("; ?", "?").replace(": ?", "?").replace(", !", "!").replace("; !", "!").replace(": !", "!")
        
        return self.runTrueCaser(s_sentence), self.runTrueCaser(s_sentence2)


    def print_sentence_appos(self, final_root, final_appos, final_subj, v_tense, n_num, subj_word):
        """
        TODO: this part is hard-coded for demonstration purposes. Need to find a resource that, given the n_num and v_tense conjugates the verb properly.
        Finalise the simplification process for appostive phrases.
        @param final_root: dictionary of the root relation
        @param final_appos: dictionary of appositive phrase
        @param final_subj: dictionary of the subject relation
        @param v_tense: verb tense
        @param n_num: subject number
        @param subj_word: head of the subject
        @return: two sentences, one for each clause.
        """
        s_sentence = ''
        s_sentence2 = ''
        for k in sorted(final_root.keys()):
            s_sentence += final_root[k] + " "

        for k in sorted(final_subj.keys()):
            s_sentence2 += final_subj[k] + " "

        ## hard-coded for demo
        # s_sentence2 += "és ".decode('utf-8')
        
        ## a line like this with the right resource should solve the problem
        #s_sentence2 += es.verb_conjugate("ser", v_tense) + " "

        ## from English simplifier --> left here as an example
        #if n_num in ("NN", "NNP"):
        #    if v_tense in ("VBP", "VBZ", "VB"):
        #        s_sentence2 += "is "
        #    elif v_tense in ("VBD", "VBG", "VBN"):
        #        s_sentence2 += "was "

        #elif n_num in ("NNS", "NNPS"):
        #    if v_tense in ("VBP", "VBZ", "VB"):
        #        s_sentence2 += "are "
        #    elif v_tense in ("VBD", "VBG", "VBN"):
        #        s_sentence2 += "were "

        #elif n_num in ("PRP") and subj_word.lower() == "they":

        #    if v_tense in ("VBP", "VBZ", "VB"):
        #        s_sentence2 += "are "
        #    elif v_tense in ("VBD", "VBG", "VBN"):
        #        s_sentence2 += "were "

        #elif n_num in ("PRP"):
        #    if v_tense in ("VBP", "VBZ", "VB"):
        #        s_sentence2 += "is "
        #    elif v_tense in ("VBD", "VBG", "VBN"):
        #        s_sentence2 += "was "

        for k in sorted(final_appos.keys()):
            s_sentence2 += final_appos[k] + " "

        ## including final punctuation
        if final_root[sorted(final_root.keys())[-1]] not in (".", "?", "!"):
            s_sentence+= ". "

        if final_subj[sorted(final_subj.keys())[-1]] not in (".", "?", "!"):
            s_sentence2+= ". "
        
        return self.runTrueCaser(s_sentence), self.runTrueCaser(s_sentence2)

    def print_sentence_voice(self, final_subj, final_obj, verb, verb_tense, v_aux,  v_tense, subj_tag, subj_word, final_mod2=None, final_root=None):
        """
        TODO: probably find a different resource to conjugate verbs --> parser POS tags have missing information (such as plural)
        Print final sentence simplified from passive voice.
        @param final_subj: dictionary with the words of the subject
        @param final_obj: dictionary with the words of the object
        @param verb: the verb of the sentence
        @param verb_tense: verb tense
        @param v_aux: auxiliary verb
        @param v_tense: auxiliary verb tense
        @param subj_tag: POS tag of the head word of the subject
        @param subj_word: head of the subject
        @param final_mod2: dictionary with the words of the mod structure
        @param final_root: dictionary with the words on the root structure
        @return simplified sentence
        """

        s_sentence1 = s_sentence2 = ''

        new_verb = es.verb_conjugate(verb, verb_tense, v_tense) + " "

        if new_verb.strip() == "":
            new_verb = es.verb_conjugate(verb, verb_tense, "vmis3s0").decode('utf8') + " "

        # modal verbs "han sido controladas" --> "han controlado" -- not working properly
        #if v_aux != None:
        #    new_verb = v_aux + " " + new_verb


        for k in sorted(final_subj.keys()):
            s_sentence1 += final_subj[k] + " "

        for k in sorted(final_obj.keys()):
            s_sentence2 += final_obj[k] + " "

        if final_mod2 != None:
            for k in sorted(final_mod2.keys()):
                s_sentence2 += final_mod2[k] + " "
        if final_root != None:
            for k in sorted(final_root.keys()):
                s_sentence2 += final_root[k] + " "


        #removing errors in punctuation
        s_sentence1 = s_sentence1.replace(", .", ".").replace("; .", ".").replace(": .", ".").replace(", ?", "?").replace("; ?", "?").replace(": ?", "?").replace(", !", "!").replace("; !", "!").replace(": !", "!").replace(". .", ".")
        s_sentence2 = s_sentence2.replace(", .", ".").replace("; .", ".").replace(": .", ".").replace(", ?", "?").replace("; ?", "?").replace(": ?", "?").replace(", !", "!").replace("; !", "!").replace(": !", "!").replace(". .", ".")


        return self.runTrueCaser(s_sentence1 + new_verb + s_sentence2)
