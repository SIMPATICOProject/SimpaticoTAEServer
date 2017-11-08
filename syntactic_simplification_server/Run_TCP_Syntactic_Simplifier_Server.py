#!/usr/bin/python
# -*- coding: latin-1 -*-
import socket
import json
import sys
sys.path[0:0] = ["simpatico_ss"]
from simpatico_ss.util import Parser
from simpatico_ss_gl.util import Parser as Parser_gl
from simpatico_ss_es.util import Parser as Parser_es
from simpatico_ss_it.util import Parser as Parser_it
import simpatico_ss.simplify
import simpatico_ss_gl.simplify
import simpatico_ss_es.simplify
import simpatico_ss_it.simplify


def getEnglishSyntacticSimplifier(resources):
    stfd_parser = Parser(resources["corenlp_dir"], resources["prop_en"])
    return simpatico_ss.simplify.Simplify(stfd_parser, resources["true_en"])

def getGalicianSyntacticSimplifier(resources):
    stfd_parser = Parser_gl(resources["corenlp_dir"], resources["prop_gl"])
    return simpatico_ss_gl.simplify.Simplify(stfd_parser, resources["true_gl"])

def getSpanishSyntacticSimplifier(resources):
    stfd_parser = Parser_es(resources["corenlp_dir"], resources["prop_es"])
    return simpatico_ss_es.simplify.Simplify(stfd_parser, resources["true_es"])

def getItalianSyntacticSimplifier(resources):
    stfd_parser = Parser_it(resources["corenlp_dir"], resources["prop_it"])
    return simpatico_ss_it.simplify.Simplify(stfd_parser, resources["true_it"])


def loadResources(path):
    #Open resource file:
    f = open(path)  

    #Create resource map:
    resources = {}
    
    #Read resource paths:
    for line in f:
        data = line.strip().split('\t')
        if data[0] in resources:
            print 'Repeated resource name: ' + data[0] + '. Please change the name of this resource.'
        resources[data[0]] = data[1]
    f.close()
    
    #Return resource database:
    return resources


#Load resources:
print "Loading resources"
resources = loadResources('../resources.txt')
configurations = loadResources('../configurations.txt')

# print resources
# print configurations

#Load simplifiers:
print "Loading English simplifier"
ss_eng = getEnglishSyntacticSimplifier(resources)

# print "Loading Galician simplifier"
# ss_eng_gl = getGalicianSyntacticSimplifier(resources)

print "Loading Spanish simplifier"
ss_eng_es = getSpanishSyntacticSimplifier(resources)

print "Loading Italian simplifier"
ss_eng_it = getItalianSyntacticSimplifier(resources)

#Wait for simplification requests:
print "Starting webserver"
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', int(configurations['ss_local_server_port'])))
serversocket.listen(5)

print "Simplification server ready!"

#Upon receival of simplification request, do:
while 1:
    #Open connection:
    (conn, address) = serversocket.accept()

    #Parse request:
    data = json.loads(conn.recv(1024).decode("utf-8"))
    sent = data['sentence']
    lang = data['lang']

    print "Sentance Received : " + sent
    print "Language :" + lang

    #Syntactic Simplification:
    if lang == 'es':
        ss_output = ss_eng_es.simplify(sent.encode("utf-8"))
    if lang == 'it':
        ss_output = ss_eng_it.simplify(sent)
    if lang == 'en':
        ss_output = ss_eng.simplify(sent.encode("utf-8"))
    elif lang == 'gl':
        ss_output = ss_eng_gl.simplify(sent)

                                                                    

    #Send result:
    conn.send(ss_output)
    conn.close()
