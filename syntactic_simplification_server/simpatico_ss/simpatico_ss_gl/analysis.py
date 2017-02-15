class Analysis():

    def __init__(self, sentence, cc, relpron):
        """
        Perform the analyses check for syntactic simplification for Galician.
        TODO: does not work here! This class is only used for analysis of relative and conjoint clauses and there is no support for these in the Galician parser.
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
                if (c>0) and (s.lower() =="if"):
                    c+=1
                else:
                    c+=1
                    if s.lower() in self.cc and "this was " + s.lower() not in " ".join(self.sentence).lower() and "this is " + s.lower() not in " ".join(self.sentence).lower() and "this happens " + s.lower() not in " ".join(self.sentence).lower() and "this happened " + s.lower() not in " ".join(self.sentence).lower()  and "this would happen " + s.lower() not in " ".join(self.sentence).lower() and "this will happen " + s.lower() not in " ".join(self.sentence).lower() and "this should happen " + s.lower() not in " ".join(self.sentence).lower() and "this could happen " + s.lower() not in " ".join(self.sentence).lower() + "this must happen " + s.lower() not in " ".join(self.sentence).lower() and "this may happen " + s.lower() not in " ".join(self.sentence).lower() and "this can happen " + s.lower() not in " ".join(self.sentence).lower() and "this shall happen " + s.lower() not in " ".join(self.sentence).lower() and "this will happen " + s.lower() not in " ".join(self.sentence).lower() and "this 'll happen " + s.lower() not in " ".join(self.sentence).lower():
                    #if s.lower() in self.cc and "this" not in " ".join(self.sentence).lower() and "happen" not in " ".join(self.sentence).lower():  
                    
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

