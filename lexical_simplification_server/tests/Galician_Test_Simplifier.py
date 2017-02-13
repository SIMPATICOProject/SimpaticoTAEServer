# -*- coding: utf-8 -*-
import socket, json

info = {}
info['sentence'] = 'Os líquens que medran no residuo asfáltico suxiren a sua baixa toxicidade , que cabería comparar á dunha autoestrada .'
info['target'] = info['sentence'].split(' ')[11]
info['index'] = '11'
info['lang'] = 'gl'
data = json.dumps(info)

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect(("localhost",1414))

print('Sending...')
s.send(data+'\n')
print('Receiving...')
resp = s.recv(1024).decode('utf8')
print resp
s.close()
