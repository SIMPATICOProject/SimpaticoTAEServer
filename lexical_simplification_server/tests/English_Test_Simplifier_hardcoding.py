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

token = 'b0fca5e6-557c-4281-ad57-460827535ea9'

###############################################################


###########################################################

instances = [line.strip().split('\t') for line in open('cw_list_all_services_v2.txt')]

print('Challenging:')
for instance in instances:
	sent = instance[0].strip()
	target = instance[1].strip()
	index = instance[2].strip()
	
	info = {}
	info['sentence'] = sent
	info['target'] = target
	info['index'] = index
	info['lang'] = 'en'
	info['token'] = token
	data = json.dumps(info)
	
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	s.connect(("localhost",int(configurations['ls_local_server_port'])))

	s.send(data+'\n')
	resp = s.recv(1024).decode('utf8')
	s.close()
	print sent+'\t'+target+'\t'+index+'\t'+resp.strip()
