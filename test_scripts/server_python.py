import socket, json

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 1313))
serversocket.listen(5)

while 1:
	(conn, address) = serversocket.accept()
	data = json.loads(conn.recv(1024).decode('utf-8'))
	print 'Here is the data: ' + str(data)
