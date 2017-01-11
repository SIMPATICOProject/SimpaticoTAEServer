import socket, json

info = {}
info['sentence'] = 'This is an complex sentence .'
info['target'] = info['sentence'].split(' ')[3]
info['index'] = '3'

data = json.dumps(info)

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect(("localhost",1414))

print('Sending...')
s.send(data+'\n')
print('Receiving...')
resp = s.recv(1024).decode('utf8')
print resp
s.close()
