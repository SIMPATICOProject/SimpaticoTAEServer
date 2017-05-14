import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

import simpatico_ss.simplify
import simpatico_ss_it.simplify
import simpatico_ss_es.simplify
import argparse
from simpatico_ss.util import Parser
from simpatico_ss_it.util import Parser as Parser_it
from simpatico_ss_es.util import Parser as Parser_es



parser = argparse.ArgumentParser(description='Rule-based syntactic simplifier for the SIMPATICO project.')
parser.add_argument('-l', help='language', choices=['en', 'it', 'es'])
parser.add_argument('-d', help='document to be simplified (with one sentence per line)')
parser.add_argument('-comp', action='store_true', default=False, help='use the complexity checker sentence selection')
parser.add_argument('-conf', action='store_true', default=False, help='use the confidence model')
args = parser.parse_args()

v_args = vars(args)

doc = open(v_args['d'], "r")

comp = v_args['comp']
conf = v_args['conf']

if v_args['l'] == 'en':
    stfd_parser = Parser("../../data/stanford-corenlp-full-2016-10-31/", "../../data/english.myproperties.properties")
    simplify = simpatico_ss.simplify.Simplify(stfd_parser, "../../data/distributions.obj")

    for s in doc.readlines():
    
        simp = simplify.simplify(s.strip(), comp, conf)

        print simp

elif v_args['l'] == 'it':
    stfd_parser_it = Parser_it("../../data/stanford-corenlp-full-2016-10-31/", "../../data/italian.myproperties.properties")
    simplify = simpatico_ss_it.simplify.Simplify(stfd_parser_it, "../../data/distributions.it.obj")

    for s in doc.readlines():
        simp = simplify.simplify(s.strip(), comp)
        print simp

elif v_args['l'] == 'es':
    stfd_parser_es = Parser_es("../../data/stanford-corenlp-full-2016-10-31/", "../../data/spanish.myproperties.properties")
    simplify = simpatico_ss_es.simplify.Simplify(stfd_parser_es, "../../data/distributions.es.obj")

    for s in doc.readlines():
        simp = simplify.simplify(s.strip(), comp)
        print simp
