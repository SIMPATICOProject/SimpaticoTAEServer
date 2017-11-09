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
            s_sentence += 'Supongamos '
            s_sentence2 += 'Entonces '
        elif mark in self.concession:
            s_sentence2 += 'Pero '
        elif mark in self.time:
            if mark_pos > 1:
                if "vmif" in root_tag: 
                    s_sentence2 += 'Esto sucederá '.decode("utf-8") + mark + " "
                else:
                    s_sentence2 += 'Esto sucede ' + mark + " "
            else:

                if "vmif" in root_tag: 
                    s_sentence2 += 'Esto sucederá '.decode("utf-8") + mark + " "
                elif "vmif" in root_tag and modal != None: 
                    s_sentence2 += 'Esto ' + modal + ' suceder ' + mark + " "
                else:
                    s_sentence2 += 'Esto sucede ' + mark + " "

        elif mark in self.justify:
            s_sentence2 += 'Mientras ' 
        elif mark in self.condition2:
            s_sentence2 += 'Alternativamente '
        
        #s_sentence2 = s_sentence2.decode('utf-8')
        
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
      
        
        if n_num in ("nc0s000", "np00000"):
            if v_tense in ("vsip000", "aq0000","vmis000","vmg0000","vmif000","vmn0000","vmip000","nc0s000"):
                s_sentence2 += "es " 
            elif v_tense in ("vmp0000", "vap0000", "vsp0000","vmii000","vmg000"):
                s_sentence2 += "fue " 

        elif n_num in ("nc0p000"):
            if v_tense in ("vsip000", "aq0000","vmis000","vmg0000","vmif000","vmn0000","vmip000","nc0s000"):
                s_sentence2 += "son " #"are "
            elif v_tense in ("vmp0000", "vap0000", "vsp0000","vmii000","vmg000"):
                s_sentence2 += "fueron " # "were "

        elif n_num in ("pp000000") and subj_word.lower() == "ellos":

            if v_tense in ("vsip000", "aq0000","vmis000","vmg0000","vmif000","vmn0000","vmip000","nc0s000"):
                s_sentence2 += "son " #"are "
            elif v_tense in ("vmp0000", "vap0000", "vsp0000","vmii000","vmg000"):
                s_sentence2 += "fueron " #"were "

        elif n_num in ("pp000000"):
            if v_tense in ("vsip000", "aq0000","vmis000","vmg0000","vmif000","vmn0000","vmip000","nc0s000"):
                s_sentence2 += "es " #"is "
            elif v_tense in ("vmp0000", "vap0000", "vsp0000","vmii000","vmg000"):
                s_sentence2 += "fue " #"was "

        for k in sorted(final_appos.keys()):
            if "," in final_appos[k]: continue 
            s_sentence2 += final_appos[k] + " "
            

        ## including final punctuation
        if final_root[sorted(final_root.keys())[-1]] not in (".", "?", "!"):
            s_sentence+= ". "

        if final_subj[sorted(final_subj.keys())[-1]] not in (".", "?", "!"):
            s_sentence2+= ". "
            
        #removing errors in punctuation
        s_sentence  = s_sentence.replace(", .", ".").replace("; .", ".").replace(": .", ".").replace(", ?", "?").replace("; ?", "?").replace(": ?", "?").replace(", !", "!").replace("; !", "!").replace(": !", "!").replace(". .", ".")
        s_sentence2 = s_sentence2.replace(", .", ".").replace("; .", ".").replace(": .", ".").replace(", ?", "?").replace("; ?", "?").replace(": ?", "?").replace(", !", "!").replace("; !", "!").replace(": !", "!").replace(". .", ".")

        
        return self.runTrueCaser(s_sentence), self.runTrueCaser(s_sentence2)
    
    def print_sentence_parataxis(self, final_root, final_appos):
        """
        @param final_root: dictionary of the root relation
        @param final_appos: dictionary of appositive phrase
        @return: two sentences, one for each clause.
        """
        s_sentence = ''
        s_sentence2 = ''
        
        s_sentence2 += ' El cual '
        
        ## build first sentence     
        for k in sorted(final_root.keys()):
            s_sentence += final_root[k] + " "
            
        ## build second sentence       
        for k in sorted(final_appos.keys()):
            s_sentence2 += final_appos[k] + " "
            
        
        ## including final punctuation
        if final_root[sorted(final_root.keys())[-1]] not in (".", "?", "!"):
            s_sentence+= " . "
        if final_appos[sorted(final_appos.keys())[-1]] not in (".", "?", "!"):
            s_sentence2+= " . "
            
        #removing errors in punctuation
        s_sentence  = s_sentence.replace(", .", ".").replace("; .", ".").replace(": .", ".").replace(", ?", "?").replace("; ?", "?").replace(": ?", "?").replace(", !", "!").replace("; !", "!").replace(": !", "!").replace(". .", ".")
        s_sentence2 = s_sentence2.replace(", .", ".").replace("; .", ".").replace(": .", ".").replace(", ?", "?").replace("; ?", "?").replace(": ?", "?").replace(", !", "!").replace("; !", "!").replace(": !", "!").replace(". .", ".")

        
        return self.runTrueCaser(s_sentence), self.runTrueCaser(s_sentence2)

    def print_sentence_voice(self, final_subj, final_obj, verb, verb_tense, v_aux, v_auxpass,  v_tense, subj_tag, subj_word, article,  final_mod2=None, final_root=None):
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
        @param article: article of the noun
        @param final_mod2: dictionary with the words of the mod structure
        @param final_root: dictionary with the words on the root structure
        @return simplified sentence
        """
        s_sentence1 = s_sentence2 = ''
        
        new_verb = es.verb_conjugate_ADDPersonNumber(verb, verb_tense, article, v_auxpass).lower() + " "

        if new_verb.strip() == "":
            print "\t\tNO VERB CONJUGATION:\t" ,   verb, verb_tense, v_tense
        else: 
            new_verb = new_verb.decode("utf-8")
             
        if v_aux != None:
            new_verb = v_aux + " " + new_verb + " "


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
