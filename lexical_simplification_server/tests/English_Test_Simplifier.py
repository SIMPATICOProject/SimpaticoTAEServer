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

#Test word hardcoding:
info = {}
info['sentence'] = 'difficulties with your landlord , or keeping up your tenancy'
info['target'] = info['sentence'].split(' ')[0]
info['index'] = '0'
info['lang'] = 'en'
info['token'] = token
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

info = {}
info['sentence'] = 'Universal Credit ( provided you have an annual net earned income of no more than # 7,400 , as assessed by earnings from up to three of your most recent assessment periods )'
info['target'] = info['sentence'].split(' ')[3]
info['index'] = '3'
info['lang'] = 'en'
info['token'] = token
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

info = {}
info['sentence'] = 'If you have a child attending a Sheffield school or maintained nursery and receive these benefits , you may be entitled to free school meals :'
info['target'] = info['sentence'].split(' ')[5]
info['index'] = '5'
info['lang'] = 'en'
info['token'] = token
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

info = {}
info['sentence'] = 'If you have a child attending a Sheffield school or maintained nursery and receive these benefits , you may be entitled to free school meals :'
info['target'] = info['sentence'].split(' ')[10]
info['index'] = '10'
info['lang'] = 'en'
info['token'] = token
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

#Test word:

info = {}
info['sentence'] = 'At least every 4 years or whenever the Council wishes to amend its Scheme , an Independent Remuneration Panel has to consider the Scheme and make recommendations to the Council .'
info['target'] = info['sentence'].split(' ')[11]
info['index'] = '11'
info['lang'] = 'en'
info['token'] = token
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

#Test word:

info = {}
info['sentence'] = 'Make sure your child s name is placed on the register at the Learning Destination , and they ll send us their register to let us know to award credits .'
info['target'] = info['sentence'].split(' ')[28]
info['index'] = '28'
info['lang'] = 'en'
info['token'] = token
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
info['token'] = token
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
