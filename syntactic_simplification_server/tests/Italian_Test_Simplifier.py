#!/usr/bin/python
# -*- coding: latin-1 -*-
import socket, json
import sys

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

configurations = loadResources('../../configurations.txt')

doc = open('examples.it', "r")

for s in doc.readlines():
    info = {}
    info['sentence'] = s.strip()
    info['lang'] = 'it'
    info['comp'] = 'False'
    info['conf'] = 'False'

    data = json.dumps(info)

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    s.connect(("localhost",int(configurations['ss_local_server_port'])))

    print('Sending...')
    s.send(data+'\n')
    print info['sentence']
    print('Receiving...')
    resp = s.recv(1024).decode('utf8')
    print resp
    print
    s.close()
