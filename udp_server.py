import socket
import struct
from timeit import default_timer as timer

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
        start = timer()
        data, addr = sock.recvfrom(10000, socket.MSG_PEEK)

        if (data): 
            mtu = True
            data = struct.unpack('II', data)
            mtu, total_packets = data[0], data[1]
            print("received init from", addr)
            sock.sendto("1".encode(), addr)  
        end = timer()
        rtt = end - start
        print("RTT = " + str(rtt))
        # begin receiving flood
        # record time
        # record received = total packets
        # how do we know when to stop
        # if empty for 5 second we stop
        time = list()
        # whenever received, we add to time

        start = timer()
        timeout_start = timer()
        while True:
            
            data, addr = sock.recvfrom(mtu)

            print("received message: "+str(len(data)))

    # data, addr = 
    # while True:
    #     data, addr = sock.recvfrom(4096)
    #     sock.sendto(data, addr)                                                                                            
    #     print("received message: "+str(len(data)))  

if __name__ == "__main__":
    #reodering_udp_scenario()
    varying_mtu_udp_scenario()