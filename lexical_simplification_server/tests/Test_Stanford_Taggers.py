# -*- coding: utf-8 -*-
import socket, json

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

def getTaggedSentences(sents, configurations, lang):
        tagged_sents = []
        for sent in sents:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.connect((configurations[lang+'_stanford_tagger_host'], int(configurations[lang+'_stanford_tagger_port'])))
                sinput = sent+'\n'
                s.send(sinput.encode("utf-8"))
                resp = [token.split(r'_') for token in s.recv(2014).decode('utf-8').strip().split(' ')]
                resp = [(token[0], token[1]) for token in resp]
                tagged_sents.append(resp)
        return tagged_sents

configurations = loadResources('../../configurations.txt')

sents = ['os prognósticos confirmaron-se e , en total , 2.100 bañistas'.decode('utf8')]

tagged = getTaggedSentences(sents, configurations, 'gl')

print tagged
