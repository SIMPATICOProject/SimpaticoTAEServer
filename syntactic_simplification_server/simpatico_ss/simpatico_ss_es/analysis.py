#!/usr/bin/python
# -*- coding: latin-1 -*-

class Analysis():

    def __init__(self, sentence, cc, relpron):
        """
        Perform the analyses check for syntactic simplification.
        @param sentence: sentence to be checked.
        @param cc: conjoint clauses makers.
        """
        self.sentence = sentence
        self.cc = cc
        self.relpron = relpron

    def analyse_cc(self):
        """
        Analyse sentences searching for markers that could indicate conjoing clauses.
        @return: a flag indicating whether or not a maker was identified and a list of markers found (None if flag = False).
        """

        if any([s.lower() in self.cc for s in self.sentence]):
            mark = []
            c = 0
            for s in self.sentence:
                if (c>0) and (s.lower() =="si"): 
                    c+=1
                else:
                    c+=1
                    if s.lower() in self.cc and "esto sucederá ".decode("utf-8") + s.lower() not in " ".join(self.sentence).lower() and "esto sucede " + s.lower() not in " ".join(self.sentence).lower() and "esto podría suceder ".decode("utf-8") + s.lower() not in " ".join(self.sentence).lower() and "esto puede suceder " + s.lower() not in " ".join(self.sentence).lower() and "esto podría suceder ".decode("utf-8")  + s.lower() not in " ".join(self.sentence).lower():
                        mark.append(s.lower())
            return True, mark
        else: 
            return False, None

    def analyse_rc(self):
        """
        Analyse sentences searching for pronouns that could indicate relative clauses.
        @return: a flag indicating whether or not a pronouns was identified and a list of pronouns found (None if flag = False).
        """
        if any([s.lower() in self.relpron for s in self.sentence]):
            mark = []
            for s in self.sentence:
                if s.lower() in self.relpron:
                    mark.append(s.lower())
            return True, mark
        else:
            return False, None

