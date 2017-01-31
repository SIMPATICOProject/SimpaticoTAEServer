import socket, json

info = {}
info['sentence'] = 'Os liquens que medran no residuo asfaltico suxiren a sua baixa toxicidade , que caberia comparar a dunha autoestrada .'
info['target'] = info['sentence'].split(' ')[7]
info['index'] = '7'
info['lang'] = 'pt'
data = json.dumps(info)

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect(("localhost",1414))

print('Sending...')
s.send(data+'\n')
print('Receiving...')
resp = s.recv(1024).decode('utf8')
print resp
s.close()
