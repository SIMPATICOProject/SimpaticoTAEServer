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

###############################################################

#Test word:

info = {}
info['sentence'] = 'This is a sample sentence for parents .'
info['target'] = info['sentence'].split(' ')[6]
info['index'] = '6'
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

###############################################################

#Test phrase:

info = {}
info['sentence'] = 'This sentence is even ever more difficult .'
info['target'] = 'even ever more difficult'
info['index'] = '3'
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
