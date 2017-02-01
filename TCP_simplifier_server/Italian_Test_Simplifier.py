# -*- coding: utf-8 -*-
import socket, json

info = {}
info['sentence'] = 'gestione dati del nucleo familiare in caso di casa famiglia ( nucleo familiare ) - da collegamento all’ anagrafe .'
info['target'] = info['sentence'].split(' ')[16]
info['index'] = '16'
info['lang'] = 'it'
data = json.dumps(info)

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect(("localhost",1616))

print('Sending...')
s.send(data+'\n')
print('Receiving...')
resp = s.recv(1024).decode('utf8')
print resp
s.close()
