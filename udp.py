import socket
from tabnanny import check
import time
import os
import struct
import timeit
from utils import rbt, network
from collections import deque
from pathlib import Path
import random

# no frills: done
# varying mtu
# compression
# reliability (randomly drop some): partial
# tls
# congestion
# multiple parallel

def no_frills_udp_client():
    UDP_PORT = 55681
    with open(os.path.join('./data/', 'video.mp4'), 'rb') as f:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket
        client_socket.settimeout(5.0)
        # IP address of the server (current machine)
        serverIP = socket.gethostbyname(socket.gethostname())

        start = time.time()
        message = f.read(4096)

        print("sending: "+str(len(message)))
        client_socket.sendto(message, (serverIP, UDP_PORT))
        try:
            data, server = client_socket.recvfrom(4096)
            end = time.time()
            elapsed = end - start
            print("Received reply!")
            print(len(data))
        except socket.timeout:
            print('REQUEST TIMED OUT')

def packet_ordering_udp_client(MTU=1472):
    serverIP = socket.gethostbyname(socket.gethostname())
    input_path = os.path.join('./data/', 'test.file')

    with open(input_path, 'rb') as f:
        size = Path(input_path).stat().st_size
        total_packets = int(size/MTU) + 1

        # identify route
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((serverIP, 6789))
        q = deque()
        s = struct.Struct('!IHH')

        # sequencing, this will be done on receiving side
        seq = 1
        while seq <= total_packets:
            # payload = f.read(5)
            payload = "WDFBBQ".encode()
            packet = network.create_packet(s, seq, payload, total_packets)
            sock.sendto(packet, (serverIP, 6789))
            q.append(packet)
            print("packet sent")
            seq += 1
        return

        # re odering
        tree = None
        pos = dict()
        arr = None
        count = 0
        while (q):  
            packet = q.pop()
            seq, chk, pck, data = network.dessemble_packet(packet)

            if (not tree): # first time we init everything
                arr = [None]*(pck+1)
                tree = rbt.RedBlackTree()
                for i in range(1, pck+1):
                    if (i == seq): continue
                    node = tree.insert(i)
                    pos[i] = node
                arr[seq] = data
                
            else: # subsequent times, if correct checksum, we remove it and put in re order array
                # if (random.random() > 0.9): 
                #   count += 1
                #   continue # simulate dropped
                if (network.calculate_checksum(data) == chk):
                  tree.delete_obj(pos[seq])
                  arr[seq] = data
                # else:
                #   print()
                  # send back request

        print(tree.size - 1)
        checker = 0
        for i in range(1,len(arr)):
          if (arr[i] == None): 
            print(i)
            checker += 1
        print(checker)

# for experiment to suceed, we need to check that all packets are received
# we dont request for resend, we just record lost packet % and time taken
# 
def varying_mtu_udp_client():
    PORT = 7890
    MTUS = [128,256,512,1024,1472,2048,4096,6144,8192,10240]
    serverIP = socket.gethostbyname(socket.gethostname())
    input_path = os.path.join('./data/', 'test.file')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((serverIP, PORT))

    size = Path(input_path).stat().st_size
    for mtu in MTUS:
      seq = 1
      with open(input_path, 'rb') as f:
        total_packets = int(size/mtu) + 1
        # we have to send a prior packet to inform mtu
        print("Sending initial")
        sock.send(mtu.to_bytes(2, 'big'))
        # sock.sendto(mtu, (serverIP, PORT))
        print("waiting reply")
        # wait for acknowledgement before start
        flag = False
        while not flag:
          data = sock.recv(mtu, socket.MSG_PEEK)
          if (data): flag = True
          print("received acknowledgement!")
          print(data)
        break
      
        # try:
        #     data, server = client_socket.recvfrom(4096)
        #     end = time.time()
        #     elapsed = end - start
        #     print("Received reply!")
        #     print(len(data))
        # except socket.timeout:
        #     print('REQUEST TIMED OUT')

        # payload = f.read(mtu)
        # packet = network.create_packet(sock, seq, payload, total_packets)
        # sock.sendto(packet, (serverIP, 6789))

        # seq += 1



if __name__ == "__main__":
  # no_frills_udp_client()
  varying_mtu_udp_client()
  # packet_ordering_udp_client(1472)
