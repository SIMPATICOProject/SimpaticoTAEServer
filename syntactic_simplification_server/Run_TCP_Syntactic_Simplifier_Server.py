#!/usr/bin/python
# -*- coding: latin-1 -*-
import socket
import json
import sys
sys.path[0:0] = ["simpatico_ss"]
from simpatico_ss.util import Parser
from simpatico_ss_gl.util import Parser as Parser_gl
from simpatico_ss_es.util import Parser as Parser_es
import simpatico_ss.simplify
import simpatico_ss_gl.simplify
import simpatico_ss_es.simplify

def getEnglishSyntacticSimplifier(resources):
    stfd_parser = Parser(resources["corenlp_dir"], resources["prop_en"])
    return simpatico_ss.simplify.Simplify(stfd_parser, resources["true_en"])

def getGalicianSyntacticSimplifier(resources):
    stfd_parser = Parser_gl(resources["corenlp_dir"], resources["prop_gl"])
    return simpatico_ss_gl.simplify.Simplify(stfd_parser, resources["true_gl"])

def getSpanishSyntacticSimplifier(resources):
    stfd_parser = Parser_es(resources["corenlp_dir"], resources["prop_es"])
    return simpatico_ss_es.simplify.Simplify(stfd_parser, resources["true_es"])


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
resources = loadResources('../resources.txt')
configurations = loadResources('../configurations.txt')

#Load simplifiers:
ss_eng = getEnglishSyntacticSimplifier(resources)
ss_eng_gl = getGalicianSyntacticSimplifier(resources)
ss_eng_es = getSpanishSyntacticSimplifier(resources)

#Wait for simplification requests:
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', int(configurations['ss_local_server_port'])))
serversocket.listen(5)

#Upon receival of simplification request, do:
while 1:
    #Open connection:
    (conn, address) = serversocket.accept()

    #Parse request:
    data = json.loads(conn.recv(1024).decode("utf-8"))
    sent = data['sentence'].encode("utf-8")
    lang = data['lang']



    #Syntactic Simplification:
    if lang == 'es':
        ss_output = ss_eng_es.simplify(sent)
    if lang == 'en':
        #print sent
        ss_output = ss_eng.simplify(sent)
    elif lang == 'gl':
        ss_output = ss_eng_gl.simplify(sent)

                                                                    

    #Send result:
    conn.send(ss_output)
    conn.close()
