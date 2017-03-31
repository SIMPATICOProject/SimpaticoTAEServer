import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

import simpatico_ss.simplify
import simpatico_ss_gl.simplify
import simpatico_ss_es.simplify
import argparse
from simpatico_ss.util import Parser
from simpatico_ss_gl.util import Parser as Parser_gl
from simpatico_ss_es.util import Parser as Parser_es



parser = argparse.ArgumentParser(description='Rule-based syntactic simplifier for the SIMPATICO project.')
parser.add_argument('-l', help='language', choices=['en', 'gl', 'es'])
parser.add_argument('-d', help='document to be simplified (with one sentence per line)')

args = parser.parse_args()

v_args = vars(args)

doc = open(v_args['d'], "r")



if v_args['l'] == 'en':
    stfd_parser = Parser("../../data/stanford-corenlp-full-2016-10-31/", "../../data/english.myproperties.properties")
    simplify = simpatico_ss.simplify.Simplify(stfd_parser, "../../data/distributions.obj")

    for s in doc.readlines():
    
        simp = simplify.simplify(s.strip())

        print simp

elif v_args['l'] == 'gl':
    stfd_parser_gl = Parser_gl("../../data/stanford-corenlp-full-2016-10-31/", "../../data/galician.myproperties.properties")
    simplify = simpatico_ss_gl.simplify.Simplify(stfd_parser_gl, "../../data/distributions.gl.obj")

    for s in doc.readlines():
        simp = simplify.simplify(s.strip())
        print simp

elif v_args['l'] == 'es':
    stfd_parser_es = Parser_es("../../data/stanford-corenlp-full-2016-10-31/", "../../data/spanish.myproperties.properties")
    simplify = simpatico_ss_es.simplify.Simplify(stfd_parser_es, "../../data/distributions.es.obj")

    for s in doc.readlines():
        simp = simplify.simplify(s.strip())
        print simp
#print simp_doc

#parser = Parser(doc)

#print parser.process()

#parse_sents = parser.process()

#a = [[parser for parser in dep_graphs] for dep_graphs in parser.process()]

#for i in parse_sents:
#    for d in i:
#        for a in d.triples():
#            print a
        #for t in range(1,50):
        #    if d.contains_address(t):
        #        b = d.get_by_address(t)
        #        print b[u'word']

#print sum([[parse.tree() for parse in dep_graphs] for dep_graphs in parser.process()],[])
