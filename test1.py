import socket, struct
from utils import network

def selective_repeat_udp_server():
    PORT = 7890
    serverIP = socket.gethostbyname(socket.gethostname())
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    s = struct.Struct('!IHH')
    a = struct.Struct('!II')
    print("Selective ARQ Server Started")

    while True:
        print("Status: awaiting experiment")
        data, addr = sock.recvfrom(1500)

        if (data):
            init, total_packets = a.unpack(data)
            print("Status: received init from", addr)
            sock.sendto("1".encode(), addr)
        
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, total_packets*1500)
        print("Status: experiment started")

        count = 0
        maxSeqNum = 0
        sock.settimeout(5.0)
        
        while True:
            try:
                data, addr = sock.recvfrom(1500)
                sequenceNum, checkSum, total_packets, data = network.dessemble_packet(data)
                ack_packet = a.pack(1, sequenceNum)
                sock.sendto(ack_packet, addr)
                count += 1
                if (count%1000==0): print(count)
                
                if (count == (total_packets+1)): 
                    print("Status: all packets received, ending experiment")
                    sock.settimeout(3600)
                    count = 0
                    total_packets = 0
                    break
                
            except socket.timeout as e:
                print("Status: have not received anything in 5 secs, ending experiment")
                sock.settimeout(3600)
                break
selective_repeat_udp_server()