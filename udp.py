import socket
import argparse
import base64
import time
import sys
import os

# parser = argparse.ArgumentParser(description='UDP benchmark cli')
# parser.add_argument('--server', type=str, help='specify the server ip')
# parser.add_argument('--port', type=str, help='specify the server port')
# parser.add_argument('--file', nargs='?', type=str, help='specify the file name (if any)', default=None)
# parser.add_argument('--encode', action='store_true', help='specify the file name (if any)')

# args = parser.parse_args()

# no frills
# varying mtu
# compression
# reliability (randomly drop some)
# tls
# congestion

def flood_udp():
  UDP_PORT = 55681
  with open(os.path.join('./data/', 'video.mp4'), 'rb') as f:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket
    client_socket.settimeout(5.0)
    serverIP = socket.gethostbyname(socket.gethostname()) # IP address of the server (current machine)

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

if __name__ == "__main__":
  flood_udp()
