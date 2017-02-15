import en
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

    def removePunctuation(self, s_sentence):
        return s_sentence.replace(", ,",",").replace(", .", ".").replace("; .", ".").replace(": .", ".").replace(", ?", "?").replace("; ?", "?").replace(": ?", "?").replace(", !", "!").replace("; !", "!").replace(": !", "!")

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
            s_sentence2 += 'And '
        if mark in self.condition:
            s_sentence += 'Suppose '
            if final2[sorted(final2.keys())[0]].lower() != 'then' and 'then' not in final2.values():
                s_sentence2 += 'Then '
        elif mark in self.concession:
            s_sentence2 += 'But '
        elif mark in self.time:
            if mark_pos > 1:
                if root_tag == 'VBP' or root_tag == 'VBZ' or root_tag == 'VB':
                    s_sentence2 += 'This is ' + mark + " "
                else:
                    s_sentence2 += 'This was ' + mark + " "
            else:

                if root_tag == 'VBP' or root_tag == 'VBZ':
                    s_sentence2 += 'This happens ' + mark + " "
                elif root_tag == 'VB' and modal != None: 
                    s_sentence2 += 'This ' + modal + ' happen ' + mark + " "
                else:
                    s_sentence2 += 'This happened ' + mark + " "

        elif mark in self.justify:
            s_sentence2 += 'So '
        elif mark in self.condition2:
            s_sentence2 += 'Alternatively '
        
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
        
        s_sentence = s_sentence.replace("either ", "")
        s_sentence2 = s_sentence2.replace("either ", "")
        s_sentence = s_sentence.replace("Either ", "")
        s_sentence2 = s_sentence2.replace("Either ", "")


        s_sentence = s_sentence[0].capitalize() + s_sentence[1:]
        s_sentence2 = s_sentence2[0].capitalize() + s_sentence2[1:]
       
        #including final punctuation
        if final1[sorted(final1.keys())[-1]] not in (".", "?", "!"):
            s_sentence+= ". "

        if final2[sorted(final2.keys())[-1]] not in (".", "?", "!"):
            s_sentence2+= ". "

       
        #removing errors in punctuation
        s_sentence = self.removePunctuation(s_sentence)
        s_sentence2 = self.removePunctuation(s_sentence2)

        return self.runTrueCaser(s_sentence), self.runTrueCaser(s_sentence2)


    def print_sentence_appos(self, final_root, final_appos, final_subj, v_tense, n_num, subj_word):
        """
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


        if n_num in ("NN", "NNP"):
            if v_tense in ("VBP", "VBZ", "VB"):
                s_sentence2 += "is "
            elif v_tense in ("VBD", "VBG", "VBN"):
                s_sentence2 += "was "
            else: 
                s_sentence2 += "are "

        elif n_num in ("NNS", "NNPS"):
            if v_tense in ("VBP", "VBZ", "VB"):
                s_sentence2 += "are "
            elif v_tense in ("VBD", "VBG", "VBN"):
                s_sentence2 += "were "
            else:
                s_sentence2 += "are "

        elif n_num in ("PRP") and subj_word.lower() == "they":

            if v_tense in ("VBP", "VBZ", "VB"):
                s_sentence2 += "are "
            elif v_tense in ("VBD", "VBG", "VBN"):
                s_sentence2 += "were "

        elif n_num in ("PRP"):
            if v_tense in ("VBP", "VBZ", "VB"):
                s_sentence2 += "is "
            elif v_tense in ("VBD", "VBG", "VBN"):
                s_sentence2 += "was "
        else:
            s_sentence2 += "are "

        for k in sorted(final_appos.keys()):
            s_sentence2 += final_appos[k] + " "

        #including final punctuation
        if final_root[sorted(final_root.keys())[-1]] not in (".", "?", "!"):
            s_sentence+= ". "

        if final_subj[sorted(final_subj.keys())[-1]] not in (".", "?", "!"):
            s_sentence2+= ". "
        

        #removing errors in punctuation
        s_sentence = self.removePunctuation(s_sentence)
        s_sentence2 = self.removePunctuation(s_sentence2)

        return self.runTrueCaser(s_sentence), self.runTrueCaser(s_sentence2)

    def print_sentence_voice(self, final_subj, final_obj, verb, v_aux,  v_tense, subj_tag, subj_word, final_mod2=None, final_root=None):
        """
        Print final sentence simplified from passive voice.
        @param final_subj: dictionary with the words of the subject
        @param final_obj: dictionary with the words of the object
        @param verb: the verb of the sentence
        @param v_aux: auxiliary verb
        @param v_tense: verb tense
        @param subj_tag: POS tag of the head word of the subject
        @param subj_word: head of the subject
        @param final_mod2: dictionary with the words of the mod structure
        @param final_root: dictionary with the words on the root structure
        @return simplified sentence
        """
        new_verb = ''
        s_sentence1 = s_sentence2 = ''
        if v_tense in ('VBD'):
            new_verb = en.verb.past(verb) + " "
        elif v_tense == 'MD' :
            new_verb = v_aux.lower() + " " + en.verb.infinitive(verb) + " "      
        elif v_tense in ('VBZ', 'VBP'):
            if subj_tag in ("NNS", "NNPS"):
                new_verb = en.verb.present(verb, person=2) + " "
            elif subj_tag in ("NN", "NNP"):
                new_verb = en.verb.present(verb, person=3) + " "
            elif subj_tag in ("PRP") and subj_word.lower() in ("i", "me") and len(final_subj) == 1:
                new_verb = en.verb.present(verb, person = 1) + " "
            elif subj_tag in ("PRP") and subj_word.lower() in ("he", "she", "it", "her", "him") and len(final_subj) == 1:
                new_verb = en.verb.present(verb, person = 3) + " "
            else:
                new_verb = en.verb.present(verb, person = 2) + " "
        elif v_tense in ('VBG'):
            if subj_tag in ("NNS", "NNPS"):
                new_verb = en.verb.present(v_aux.lower(), person = 2, negate = False) + " " + en.verb.present_participle(verb) + " "
            elif subj_tag in ("NN", "NNP"):
                new_verb = en.verb.present(v_aux.lower(), person = 3, negate = False) + " " + en.verb.present_participle(verb) + " "
            elif subj_tag in ("PRP") and subj_word.lower() in ("i", "me") and len(final_subj) == 1:
                new_verb = en.verb.present(v_aux.lower(), person = 1, negate = False) + " " + en.verb.present_participle(verb) + " "
            elif subj_tag in ("PRP") and subj_word.lower() in ("he", "she", "it", "her", "him") and len(final_subj) == 1:
                new_verb = en.verb.present(v_aux.lower(), person = 3, negate = False) + " " + en.verb.present_participle(verb) + " "
            else:
                new_verb = en.verb.present(v_aux.lower(), person = 2, negate = False) + " " + en.verb.present_participle(verb) + " "

        elif v_tense in ('VBN'):
            if subj_tag in ("NNS", "NNPS"):
                new_verb = en.verb.present(v_aux.lower(), person = 2, negate = False) + " " + en.verb.past_participle(verb) + " "
            elif subj_tag in ("NN", "NNP"):
                new_verb = en.verb.present(v_aux.lower(), person = 3, negate = False) + " " + en.verb.past_participle(verb) + " "
            elif subj_tag in ("PRP") and subj_word.lower() in ("i", "me") and len(final_subj) == 1:
                new_verb = en.verb.present(v_aux.lower(), person = 1, negate = False) + " " + en.verb.past_participle(verb) + " "
            elif subj_tag in ("PRP") and subj_word.lower() in ("he", "she", "it", "her", "him") and len(final_subj) == 1:
                new_verb = en.verb.present(v_aux.lower(), person = 3, negate = False) + " " + en.verb.past_participle(verb) + " "
            else:
                new_verb = en.verb.present(v_aux.lower(), person = 2, negate = False) + " " + en.verb.past_participle(verb) + " "
        
        if subj_tag in ("PRP") and subj_word.lower() == "me" and len(final_subj) == 1:
            for k in final_subj.keys():
                final_subj[k] = "I"
        elif subj_tag in ("PRP") and subj_word.lower() == "her" and len(final_subj) == 1:
            for k in final_subj.keys():
                final_subj[k] = "she"
        elif subj_tag in ("PRP") and subj_word.lower() == "him" and len(final_subj) == 1:
            for k in final_subj.keys():
                final_subj[k] = "he"
        elif subj_tag in ("PRP") and subj_word.lower() == "them" and len(final_subj) == 1:
            for k in final_subj.keys():
                final_subj[k] = "them"
        elif subj_tag in ("PRP") and subj_word.lower() == "us" and len(final_subj) == 1:
            for k in final_subj.keys():
                final_subj[k] = "we"

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
        s_sentence1 = self.removePunctuation(s_sentence1)
        s_sentence2 = self.removePunctuation(s_sentence2)


        return self.runTrueCaser(s_sentence1 + new_verb + s_sentence2)

