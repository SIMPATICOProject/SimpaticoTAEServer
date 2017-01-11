import socket

# Set up a TCP/IP socket
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# Connect as client to a selected server
# on a specified port
s.connect(("localhost",2020))

# Protocol exchange - sends and receives
s.send('\n')
while True:
        resp = s.recv(1024)
        if resp == "": break
        print resp,

# Close the connection when completed
s.close()
print "\ndone"
