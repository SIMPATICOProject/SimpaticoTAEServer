import socket, json

info = {}
info['sentence'] = 'This, my friend, is a orthodox sentence.'
info['target'] = info['sentence'].split(' ')[5]
info['index'] = '5'
info['lang'] = 'en'
data = json.dumps(info)

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect(("localhost",1616))

print('Sending...')
s.send(data+'\n')
print('Receiving...')
resp = s.recv(1024).decode('utf8')
print resp
s.close()
