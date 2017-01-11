import socket

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect(("localhost",1313))

s.send('["foo", {"bar":["baz", null, 1.0, 2]}]\n')
#while True:
#        resp = s.recv(1024)
#        if resp == "": break
#        print resp,

s.close()
