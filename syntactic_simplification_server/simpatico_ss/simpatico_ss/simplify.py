from analysis import Analysis
from generation import Generation
from nltk.tokenize import StanfordTokenizer
from util import Parser
import string
from nltk.parse import DependencyGraph
import operator
import time
import sys
from classify import Classify
from confidence import Confidence

class Simplify():

    def __init__(self, parser, truecase_model, lm, conf_model, comp_model):
        """
        Perform syntactic simplification rules.
        @param parser: parser server.
        @param truecase_model: truecase model.
        """
        #self.sentences = open(doc, "r").read().strip().split("\n")
        ## markers are separated by their most used sense
        self.time = ['when', 'after', 'since', 'before', 'once']
        self.concession = ['although', 'though', 'but', 'however', 'whereas']
        self.justify = ['because', 'so', 'while']
        self.condition = ['if']
        self.condition2 = ['or']
        self.addition = ['and']
        
        ## list of all markers for analysis purposes
        self.cc = self.time + self.concession + self.justify + self.condition + self.addition + self.condition2

        ## list of relative pronouns
        self.relpron = ['whom', 'whose', 'which', 'who']

        ## initiates parser server
        self.parser = parser
        
        ## Generation class instance
        self.generation = Generation(self.time, self.concession, self.justify, self.condition, self.condition2, self.addition, self.cc, self.relpron, truecase_model)
        
        self.lm = lm
        self.conf_model = conf_model
        self.comp_model = comp_model
        

        
    def transformation(self, sent, ant, comp=False, justify=False):
        """
        Transformation step in the simplification process.
        This is a recursive method that receives two parameters:
        @param sent: sentence to be simplified.
        @param ant: previous sentence. If sent = ant, then no simplification should be performed.
        @param justify: controls cases where sentence order is inverted and should invert the entire recursion.
        @return: the simplified sentences.
        """

        def remove_all(aux, item):
            """
            Remove all incidences of a node in a graph (needed for graphs with cycles).
            @param aux: auxiliary of parse structure
            @param item: node to be removed
            """
            for a in aux.keys():
                for d in aux[a].keys():
                    if item in aux[a][d]:
                        aux[a][d].remove(item)



        def recover_punct(final, s):
            """
            Recover the punctuation of the sentence (needed because the dependency parser does not keep punctuation.
            @param final: the final dictionary with the words in order
            @param s: the tokenised sentence with the punctuation marks
            @return the final dictionary with the punctuation marks
            """

            char_list = "``\'\'"
            ant = 0
            for k in sorted(final.keys()):
                if int(k) - ant == 2 :
                    if s[k-2] in string.punctuation + char_list:
                        final[k-1] = s[k-2]
                    elif s[k-2] == "-RRB-":
                        final[k-1] = ")"
                    elif s[k-2] == "-LRB-":
                        final[k-1] = "("
                if int(k) - ant == 3 :
                    if s[k-2] in string.punctuation + char_list and s[k-3] in string.punctuation + char_list:
                        final[k-1] = s[k-2]
                        final[k-2] = s[k-3]
                ant = k
            return final


        def build(root, dep, aux, words, final, yes_root=True, previous=None):
            """
            Creates a dictionary with the words of a simplified clause, following the sentence order.
            This is a recursive method that navigates through the dependency tree.
            @param root: the root node in the dependency tree
            @param dep: the dependencies of the root node
            @param aux: the auxiliary parser output
            @param words: auxiliary parsed words
            @param final: dictionary with the positions and words
            @param yes_root: flag to define whether or not the root node should be included
            @param previous: list of nodes visited
            """

            ## controls recursion    
            if previous == None:
                previous = []
            
            if root in previous:
                return
            
            previous.append(root)

            ## for cases where the rule does not include the root node
            if yes_root: 
                final[root] = words[root-1][0]
                previous.append(root)

            for k in dep.keys():
                for i in dep[k]:
                    if i in aux.keys():

                        deps = aux[i]
                        
                        ## needed for breaking loops -- solved by the recursion condition
                        #for d in deps.keys():
                        #    if i in deps[d]:
                        #        deps[d].remove(i)
                        
                        build(i, deps, aux, words, final,previous=previous)

                    final[i] = words[i-1][0]



        def conjoint_clauses(aux, words, root, deps_root, ant, _type, rel):
            """
            Simplify conjoint clauses
            @param aux: auxiliary parser output
            @param words: auxiliary words and POS tags structure
            @param root: root node in the dependency tree
            @param deps_root: dependencies of the root node
            @param ant: previous sentence (for recursion purposes)
            @param _type: list of markers found in the sentence that can indicate conjoint clauses
            @param rel: parser relation between the main and the dependent clause (can be 'advcl' or 'conj')
            @return: a flag that indicates whether or not the sentence was simplified and the result sentence (if flag = False, ant is returned)
            """
            
            ## split the clauses
            others = deps_root[rel]
            pos = 0
            s1 = s2 = ""
            v_tense = ""
            for o in others:
                flag = True
                if o not in aux:
                    flag = False
                    continue
                deps_other = aux[o]
                
                ## hack for relations that we don't want to process (such as advcl:under) -- mistakes from the parser
                #if ":" in rel:

                #    if rel[:-1].split(":")[1] in ("under", "over"):
                #        flag = False
                #        continue

                ## check the marker position ('when' is advmod, while others are mark)
                if 'advcl' in rel:
                    if 'mark' in deps_other.keys():
                        mark = deps_other['mark'][0]
                        mark_name = words[mark-1][0].lower()
                    elif 'advmod' in deps_other.keys():
                        mark = deps_other['advmod'][0]
                        mark_name = words[mark-1][0].lower()
                    else:
                        flag = False #needed for broken cases
                        continue
                else:
                    if 'cc' in deps_root.keys() and 'conj' in rel:
                        conj = deps_root[rel][0]
                        if 'VB' in words[conj-1][1]['PartOfSpeech'] and 'VB'in words[root-1][1]['PartOfSpeech']: #needed for broken cases like 'Care and support you won't have to pay towards'
                            mark = deps_root['cc'][0]
                            mark_name = words[mark-1][0].lower()
                        else:
                            flag = False
                            continue
                    else:
                        flag = False
                        continue
                
                ## hack for simpatico use cases
                if mark_name == "and" and words[mark-2][0].lower() == "care" and words[mark][0].lower() == "support":
                    flag = False
                    continue

                ## dealing with cases without subject 
                if 'nsubj' not in deps_other and 'nsubj' in deps_root:
                    deps_other['nsubj'] = deps_root['nsubj']
                elif 'nsubj' not in deps_other and 'nsubjpass' in deps_root:
                    deps_other['nsubj'] = deps_root['nsubjpass']
                elif 'nsubj' not in deps_other and 'nsubj' not in deps_root:
                    flag = False
                    continue
                
                ## check if the marker is in the list of selected markers
                if mark_name in _type:
                    
                    ## check if verbs have objects
                    tag_list = ('advcl', 'xcomp', 'acomp', 'amod', 'appos', 'cc', 'ccomp', 'dep', 'dobj', 'iobj', 'nwe', 'pcomp', 'pobj', 'prepc', 'rcmod', 'ucomp', 'nmod', 'auxpass', 'advmod', 'prep')

                    #if not any([t in tag_list  for t in deps_root.keys()]):
                        #return False, ant
                    #    flag = False
                    #    continue
                    #elif not any([t in tag_list  for t in deps_other.keys()]):
                        #return False, ant
                    #    flag = False
                    #    continue
                    #if (len(deps_root) < 2 or len(deps_other) < 2):
                    #   return False, ant
                    
                    ## delete marker and relation from the graph
                    if 'advcl' in rel:
                        if 'mark' in deps_other.keys():
                             del deps_other['mark'][0]
                        elif 'advmod' in deps_other.keys():
                            del deps_other['advmod'][0]
                    else:
                        del deps_root['cc'][0]
                                
                    #del deps_root[rel][pos]
                    #pos+=1


                    deps_root[rel].remove(o)

                    ## for cases with time markers -- This + modal + happen
                    modal = None
                    if 'aux' in deps_root and mark_name in self.time:
                        modal_pos = deps_root['aux'][0]
                        modal = words[modal_pos-1][0]

                    ## for cases either..or with the modal verb attached to the main clause
                    if 'aux' in deps_root and mark_name in self.condition2:
                        deps_other['aux'] = deps_root[u'aux']
                  
                    
                    ## build the sentence again
                    final_deps = {}
                    build(o, deps_other, aux, words, final_deps)

                    ## hack to correct problems with the "if" rule
                    if "advcl:if" in rel:
                        for d in deps_root.keys():
                            if "advcl:if" in d:
                                for o in deps_root[d]:
                                    deps_root[d].remove(o)

                    ## build the sentence again                
                    final_root = {}
                    build(root, deps_root, aux, words,  final_root)



                    
                    ## TODO: remove this part from here --> move to another module: self.generation
                    root_tag =  words[root-1][1]['PartOfSpeech']
                    justify = True
                    #if ((root > o) and (mark_name in self.time and mark>1)) or (mark_name == 'because' and mark > 1):
                    if (root > o) or (mark_name == 'because' and mark > 1):
                        if (mark_name in self.time and mark == 1):
                            sentence1, sentence2 = self.generation.print_sentence(final_root, final_deps, root_tag, mark_name, mark, modal)
                        else:
                            sentence1, sentence2 = self.generation.print_sentence(final_deps, final_root, root_tag, mark_name, mark, modal)
                    else:
                        sentence1, sentence2 = self.generation.print_sentence(final_root, final_deps, root_tag, mark_name, mark, modal)
                        
                    s1 = self.transformation(sentence1, ant, justify=justify)
                    s2 = self.transformation(sentence2, ant)

                    flag = True 
                else:
                    flag = False
                    continue
            
            if flag:
                return flag,  s1 + s2
            else:
                return flag, ant


        def relative_clauses(aux, words, root, deps_root, ant, rel):
            """
            Simplify relative clauses
            @param aux: auxiliary parser output
            @param words: auxiliary words and POS tags structure
            @param root: root node in the dependency tree
            @param deps_root: dependencies of the root node
            @param ant: previous sentence (for recursion purposes)
            @param rel: parser relation between the main and the dependent clause (can be 'nsubj' or 'dobj')
            @return: a flag that indicates whether or not the sentence was simplified and the result sentence (if flag = False, ant is returned)
            """
            subj = deps_root[rel][0]
            if subj not in aux.keys():
                return False, ant
            deps_subj = aux[subj]
            if 'acl:relcl' in deps_subj.keys() or 'rcmod' in deps_subj.keys():
                if 'acl:relcl' in deps_subj.keys():
                    relc = deps_subj['acl:relcl'][0]
                    type_rc = 'acl:relcl'
                else:
                    relc = deps_subj['rcmod'][0]
                    type_rc = 'rcmod'
                deps_relc = aux[relc]

                if 'nsubj' in deps_relc.keys():
                    subj_rel = 'nsubj'
                elif 'nsubjpass' in deps_relc.keys():
                    subj_rel = 'nsubjpass'

                if 'ref' in deps_subj:
                    to_remove = deps_subj['ref'][0] 
                    mark = words[deps_subj['ref'][0]-1][0].lower()
                else:
                    to_remove = deps_relc[subj_rel][0]
                    mark = words[deps_relc[subj_rel][0]-1][0].lower()

                if mark in self.relpron:
                    deps_relc[subj_rel][0] = subj
                    remove_all(aux, to_remove)
                elif 'dobj' in deps_relc: ## needed for cases where the subject of the relative clause is the object
                    obj = deps_relc['dobj'][0]
                    if 'poss' in aux[obj]:
                        mod = aux[obj]['poss'][0]
                        aux_words = list(words[mod-1])
                        aux_words[0] = words[subj-1][0] + '\'s'
                        words[mod-1] = tuple(aux_words)
                        aux[mod] = aux[subj]
                    else:
                        return False, ant
                else:
                    return False, ant #for borken cases - " There are some situations where it is particularly important that you get financial information and advice that is independent of us."

                del aux[subj][type_rc]

                if 'punct' in deps_subj.keys():
                    del aux[subj]['punct']

                
                final_root= {}
                build(root, deps_root, aux, words, final_root)
                final_relc = {}
                build(relc, deps_relc, aux, words, final_relc)


                if justify:
                    sentence2, sentence1 = self.generation.print_sentence(final_root, final_relc)
                else:
                    sentence1, sentence2 = self.generation.print_sentence(final_root, final_relc)

                s1 = self.transformation(sentence1, ant, justify=justify)
                s2 = self.transformation(sentence2, ant)
                return True, s1 + " " +  s2
            else:
                return False, ant


        def appositive_phrases(aux, words, root, deps_root, ant):
            """
            Simplify appositive phrases
            @param aux: auxiliary parser output
            @param words: auxiliary words and POS tags structure
            @param root: root node in the dependency tree
            @param deps_root: dependencies of the root node
            @param ant: previous sentence (for recursion purposes)
            @return: a flag that indicates whether or not the sentence was simplified and the result sentence (if flag = False, ant is returned)
            """

            ## apposition needs to have a subject -- same subject of the mais sentence.
            if 'nsubj' in deps_root.keys():

                subj = deps_root['nsubj'][0]
                subj_word = words[subj-1][0]

                if subj not in aux:
                    return False, ant

                deps_subj = aux[subj]
                v_tense = words[root-1][1]['PartOfSpeech']
                n_num = words[subj-1][1]['PartOfSpeech']
                if 'amod' in deps_subj: ## bug -- this generates several mistakes... 
                    mod = deps_subj['amod'][0]
                    if mod in aux:
                        deps_mod = aux[mod]
                    else:
                        deps_mod = {}
                    del aux[subj]['amod']
                    deps_subj = aux[subj]
                        
                    ## Treat simple cases such as 'general rule'
                    #if 'JJ' in words[mod-1][1]['PartOfSpeech'] and len(deps_mod.keys()) == 0: 
                    if 'JJ' in words[mod-1][1]['PartOfSpeech'] and 'punct' not in deps_subj:
                        return False, ant

                elif 'appos' in deps_subj:
                    mod = deps_subj['appos'][0]
                    if mod in aux:
                        deps_mod = aux[mod]
                    else:
                        deps_mod = {}
                    del aux[subj]['appos']
                    deps_subj = aux[subj]
                else:
                    return False, ant

                if 'punct' in deps_subj.keys():
                    del deps_subj['punct']

                final_root = {}
                build(root, deps_root, aux, words, final_root)
                final_appos = {}
                build(mod, deps_mod, aux, words, final_appos)
                final_subj = {}
                build(subj, deps_subj, aux, words, final_subj)

                if len(final_appos.keys()) < 2:
                    return False, ant

                sentence1, sentence2 = self.generation.print_sentence_appos(final_root, final_appos, final_subj, v_tense, n_num, subj_word)
                s1 = self.transformation(sentence1, ant)
                s2 = self.transformation(sentence2, ant)
                return True, s1 + " " + s2
            else:
                return False, ant

        def passive_voice(aux, words, root, deps_root, ant):
            """
            Simplify sentence from passive to active voice.
            @param aux: auxiliary parser output
            @param words: auxiliary words and POS tags structure
            @param root: root node in the dependency tree
            @param deps_root: dependencies of the root node
            @param ant: previous sentence (for recursion purposes)
            @return: a flag that indicates whether or not the sentence was simplified and the result sentence (if flag = False, ant is returned)
            """

            if 'auxpass' in deps_root.keys():
                    
                if 'nmod:agent' in deps_root.keys():

                    if 'nsubjpass' not in deps_root:
                        return False, ant

                    subj = deps_root['nsubjpass'][0]
                    if subj in aux:
                        deps_subj = aux[subj]
                    else:
                        deps_subj = {}
                        
                    aux_tense = words[deps_root['auxpass'][0]-1][1]['PartOfSpeech']
                    v_aux = None

                    if aux_tense == 'VB' and 'aux' in deps_root.keys():
                        aux_tense = words[deps_root['aux'][0]-1][1]['PartOfSpeech']
                        v_aux = words[deps_root['aux'][0]-1][0]
                        del deps_root['aux']
                    elif aux_tense == 'VBG' and 'aux' in deps_root.keys():
                        #aux_tense = aux.get_by_address(deps_root[u'aux'][0])[u'tag']
                        v_aux = words[deps_root['aux'][0]-1][0]
                        del deps_root['aux']
                    elif aux_tense == 'VBN' and 'aux' in deps_root.keys():
                        #v_aux = words[deps_root['aux'][0]-1][1]['PartOfSpeech']
                        v_aux = words[deps_root['aux'][0]-1][0]
                        if v_aux.lower() in ("has", "have"):
                            v_aux = words[deps_root['aux'][0]-1][0]
                        else:
                            aux_tense = 'MD'
                        del deps_root['aux']
                           
                    del deps_root['auxpass']
                    del deps_root['nsubjpass']

                    if len(deps_root['nmod:agent']) > 1:
                        mod = deps_root['nmod:agent'][1]
                        mod2 = deps_root['nmod:agent'][0]
                        deps_mod = aux[mod]
                        deps_mod2 = aux[mod2]
                        if 'case' in deps_mod:
                            if words[deps_mod[u'case'][0]-1][0].lower() != 'by':
                                return False, ant
                            del deps_mod['case']
                            del deps_root['nmod:agent']
                            subj_tag = words[mod-1][1]['PartOfSpeech']
                            subj_word = words[mod-1][0]  
                            final_subj = {}
                            build(mod, deps_mod, aux, words, final_subj)
                                
                            final_obj = {}
                            build(subj, deps_subj, aux, words, final_obj)
                                
                            final_mod2 = {}
                            build(mod2, deps_mod2, aux, words, final_mod2)

                            final_root = {}
                            build(root, deps_root, aux, words, final_root, False)
                                
                                
                            sentence1 = self.generation.print_sentence_voice(final_subj, final_obj, words[root-1][0], v_aux, aux_tense, subj_tag, subj_word, final_mod2, final_root)
                            s1 = self.transformation(sentence1, ant)
                            return True, s1
                        elif 'case' in deps_mod2:
                            if words[deps_mod2['case'][0]-1][0].lower() != 'by':
                                return False, ant
                            del deps_mod2['case']
                            del deps_root['nmod:agent']
                            subj_tag = words[mod2-1][1]['PartOfSpeech']
                            subj_word = words[mod2-1][0]
                                
                            final_subj = {}
                            build(mod2, deps_mod2, aux, words, final_subj)
                                
                            final_obj = {}
                            build(subj, deps_subj, aux, words, final_obj)
                                
                            final_mod2 = {}
                            build(mod, deps_mod, aux, words, final_mod2)

                            final_root = {}
                            build(root, deps_root, aux, words, final_root, False)

                            sentence1 = self.generation.print_sentence_voice(final_subj, final_obj, words[root-1][0], v_aux, aux_tense, subj_tag, subj_word, final_mod2, final_root)
                            s1 = self.transformation(sentence1, ant)
                            return True, s1
                        else:
                            return False, ant

                    else:
                        mod = deps_root['nmod:agent'][0]
    
                        deps_mod =  aux[mod]

                        if 'case' in deps_mod:
                            if words[deps_mod['case'][0]-1][0].lower() != 'by':
                                return False, ant

                            del deps_mod['case']
                            del deps_root['nmod:agent']

                            subj_tag = words[mod-1][1]['PartOfSpeech']
                            subj_word = words[mod-1][0]
                    
                            final_subj = {}
                            build(mod, deps_mod, aux, words, final_subj)

                            final_obj = {}
                            build(subj, deps_subj, aux, words, final_obj)
                        
                            final_root = {}
                            build(root, deps_root, aux, words, final_root, False)

                            sentence1 = self.generation.print_sentence_voice(final_subj, final_obj, words[root-1][0], v_aux, aux_tense, subj_tag, subj_word, final_root)
                            s1 = self.transformation(sentence1, ant)
                            return True, s1
                        else:
                            return False, ant
                else: 
                    return False, ant
            else:
                return False, ant

                

        ## MAIN OF TRANSFORMATION
        
        ## control recursion: check whether there is no simplification to be done
        if sent == ant:
            return sent

        flag = False

        ant = sent


        ## parser
        try:
            parsed = self.parser.process(sent)

        except AssertionError:
            return ant

        ## data structure for the words and POS
        words = parsed['words']

        ## data structure for the dependency parser
        dict_dep = self.parser.transform(parsed)

        #print dict_dep

        ## classify whether the sentence should be simplified or not (EMNLP demo extension)
        if comp:
            c = Classify()
            label = c.classify(sent, dict_dep, words, self.comp_model)
            if label[0] == 0. : 
                return ant


        ## check whether or not the sentence has a root node
        if 0 not in dict_dep:
            return ant

        root = dict_dep[0]['root'][0]
        
        ## check for root dependencies
        if root not in dict_dep:
            return ant

        deps_root = dict_dep[root]
        
        ## get tokens
        sent_tok = []
        for w in words:
            sent_tok.append(w[0])


        ## dealing with questions
        ## TODO: improve this control with parser information.
        if sent_tok[0].lower() in ("what", "where", "when", "whose", "who", "which", "whom", "whatever", "whatsoever", "whichever", "whoever", "whosoever", "whomever", "whomsoever", "whoseever", "whereever") and sent_tok[-1] == "?":
            return ant

        ## deal with apposition
        flag, simpl = appositive_phrases(dict_dep, words, root, deps_root, ant)
        if flag:
            return simpl
        
        
        ## analyse whether or not a sentence has simplification clues (in this case, discourse markers or relative pronouns)
        a = Analysis(sent_tok, self.cc, self.relpron)

        flag_cc, type_cc = a.analyse_cc()

        ## if sentence has a marker that requires attention
        if flag_cc:
            ## sorting according to the order of the relations
            rel = {}
            for k in deps_root.keys():
                if 'conj' in k or 'advcl' in k:
                    others = sorted(deps_root[k], reverse=True)
                    cnt = 0
                    for o in others:
                        if "V" in words[o-1][1]['PartOfSpeech']:
                            deps_root[k+str(cnt)] = []
                            deps_root[k+str(cnt)].append(o)
                            rel[k+str(cnt)] = deps_root[k][0]
                            cnt+=1
                    del deps_root[k]
            
            sorted_rel = sorted(rel.items(), key=operator.itemgetter(1))
            for k in sorted_rel:
                flag, simpl = conjoint_clauses(dict_dep, words, root, deps_root, ant, type_cc, k[0])
                if flag:
                    return simpl


                    
    
        flag_rc, type_rc = a.analyse_rc()

        ## if sentence has a relative pronoun
        if flag_rc:
                
    
            ## check where is the dependency of the relative clause
            if 'nsubj' in deps_root:
                flag, simpl = relative_clauses(dict_dep, words, root, deps_root, ant, 'nsubj')
                if flag:
                    return simpl
            elif 'dobj' in deps_root:
                flag, simpl = relative_clauses(dict_dep, words, root, deps_root, ant, 'dobj')
                if flag:
                    return simpl


        


        ## deal with passive voice
        flag, simpl = passive_voice(dict_dep, words, root, deps_root, ant)
        if flag:
            return simpl

        
        ## return the original sentence if no simplification was done
        if flag== False:
            return ant

    def simplify(self, sentence, comp=False, conf=False):        
        """
        Call the simplification process for all sentences in the document.
        """
        #c = 0
        #simp_sentences = []
        #for s in self.sentences:

            #print "Original: " + s
        try:
            
            simp_sentence = self.transformation(sentence, '', comp=comp)
        
            if simp_sentence != sentence and conf == True:

                c = Confidence()
                label = c.classify(sentence,simp_sentence,self.parser,self.lm,self.conf_model)
                if label[0] == 1. : 
                    return sentence

            return simp_sentence
        except:            
            print "error exception in simplify.py "
            print sys.exc_info()
            return sentence
