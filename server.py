import socket

UDP_PORT = 55681

sock = socket.socket(socket.AF_INET, # Internet                                                                                                                       
                 socket.SOCK_DGRAM) # UDP                                                                                                                         
sock.bind(('', UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    sock.sendto(data, addr)                                                                                            
    print("received message: "+str(len(data)))