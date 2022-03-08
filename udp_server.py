import socket

def base_udp_scenario():
    UDP_PORT = 55681
    sock = socket.socket(socket.AF_INET, # Internet                                                                                                                       
                    socket.SOCK_DGRAM) # UDP                                                                                                                         
    sock.bind(('', UDP_PORT))
    print("server up")
    while True:
        data, addr = sock.recvfrom(4096)
        sock.sendto(data, addr)                                                                                            
        print("received message: "+str(len(data)))

def reodering_udp_scenario():
    UDP_PORT = 6789
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', UDP_PORT))
    print("Reodering server up")
    while True:
        data, addr = sock.recvfrom(1472)
        print("received message", len(data))

def varying_mtu_udp_scenario():
    UDP_PORT = 7890
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', UDP_PORT))
    print("Varying mtu server up")
    mtu = None

    while not mtu:
        data, addr = sock.recvfrom(10000, socket.MSG_PEEK)
        if (data): 
            mtu = True
            print(data)
            print("received acknowledgement from", addr)
            sock.sendto("1".encode(), addr)  
    # data, addr = 
    # while True:
    #     data, addr = sock.recvfrom(4096)
    #     sock.sendto(data, addr)                                                                                            
    #     print("received message: "+str(len(data)))  

if __name__ == "__main__":
    #reodering_udp_scenario()
    varying_mtu_udp_scenario()