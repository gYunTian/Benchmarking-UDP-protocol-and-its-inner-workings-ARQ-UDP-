import socket
from tabnanny import check
import time
import os
import struct
import timeit
from utils import rbt
from collections import deque
from pathlib import Path
import random

# no frills
# varying mtu
# compression
# reliability (randomly drop some)
# tls
# congestion
# multiple parallel

UDP_PORT = 55681


def calculate_checksum(packet):
    """Calculate the ICMPv6 checksum for a packet.

    :param packet: The packet bytes to checksum.
    :returns: The checksum integer.
    """
    total = 0

    # Add up 16-bit words
    num_words = len(packet) // 2
    for chunk in struct.unpack("!%sH" % num_words, packet[0:num_words * 2]):
        total += chunk

    # Add any left over byte
    if len(packet) % 2:
        total += packet[-1] << 8

    # Fold 32-bits into 16-bits
    total = (total >> 16) + (total & 0xffff)
    total += total >> 16
    return ~total + 0x10000 & 0xffff


def no_fills_udp_client():
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


def create_packet(s, seq, payload, total_packets):
    checksum = calculate_checksum(payload)
    header = s.pack(seq, checksum, total_packets)
    return (header + payload)


def dessemble_packet(packet):
    header = struct.unpack('!IHH', packet[0:8])
    sequenceNum, checkSum, total_packets, data = header[0], header[1], header[2], packet[8:]
    return sequenceNum, checkSum, total_packets, data


def packet_ordering_udp_client(MTU=1472):
    serverIP = socket.gethostbyname(socket.gethostname())
    input_path = os.path.join('./data/', 'test.txt')

    with open(input_path, 'rb') as f:
        size = Path(input_path).stat().st_size
        total_packets = int(size/MTU) + 1

        # identify route
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((serverIP, 6789))
        q = deque()
        s = struct.Struct('!IHH')

        # sequencing
        seq = 1
        while seq <= total_packets:
            # payload = f.read(5)
            payload = "WDFBBQ".encode()
            packet = create_packet(s, seq, payload, total_packets)
            q.append(packet)
            # send
            seq += 1
            # break
        
        # re odering
        tree = None
        pos = dict()
        arr = None
        count = 0
        while (q):  
            packet = q.pop()
            seq, chk, pck, data = dessemble_packet(packet)

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
                if (calculate_checksum(data) == chk):
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


        # size = os.stat(f).st_size
        # total_packets =
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # client_socket
        # client_socket.settimeout(5.0)
        # serverIP = socket.gethostbyname(socket.gethostname()) # IP address of the server (current machine)

#   UDP with checksum
#
#


if __name__ == "__main__":
    packet_ordering_udp_client(1472)
