# -*- coding: utf-8 -*-
import socket, json
from nltk.tokenize import word_tokenize

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

configurations = loadResources('../../../configurations.txt')

f = open('batch_input.txt')
for line in f:
	newsent = u''
	words = word_tokenize(line.strip().lower())
	sent = ' '.join(words)
	for i, w in enumerate(words):
		info = {}
		info['sentence'] = sent
		info['target'] = w
		info['index'] = str(i)
		info['lang'] = 'en'
		data = json.dumps(info)

		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		
		s.connect(("localhost",int(configurations['ls_local_server_port'])))
		
		s.send(data+'\n')
		resp = s.recv(1024).decode('utf8').strip()
		if resp=='NULL':
			newsent += w.decode('utf8') + ' '
		else:
			newsent += '#'+w.decode('utf8')+'#('+resp+') '
		s.close()

	print newsent
