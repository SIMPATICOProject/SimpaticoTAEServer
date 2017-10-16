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

configurations = loadResources('../../configurations.txt')

info = {}
info['sentence'] = 'This, my friend, is an orthodox sentence mañana.'
info['target'] = info['sentence'].split(' ')[5]
#info['index'] = '5'
info['lang'] = 'en'
data = json.dumps(info)
print data

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect(("localhost",int(configurations['ls_local_server_port'])))

print('Sending...')
s.send(data+'\n')
print('Receiving...')
resp = s.recv(1024).decode('utf8')
print resp
s.close()
