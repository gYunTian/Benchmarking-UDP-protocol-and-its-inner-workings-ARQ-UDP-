from timeit import default_timer as timer
import socket, time, struct, threading, logging, random, select
from utils import network, rbt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='./logs/varying_mtu.log', filemode='w')

def base_udp_scenario():
    UDP_PORT = 55681
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind(('', UDP_PORT))
    print("base no frills Server Started")
    
    total_packets = 21740
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,total_packets*1472)
    count = 0

    while True:
        try:
            data, addr = sock.recvfrom(1500)
            count += 1
            
            if (count == total_packets): 
                #print("Status: all packets received, ending experiment")
                # sock.settimeout(3600)
                count = 0
                total_packets = 0
            
        except socket.timeout as e:
            print("Status: have not received anything in 5 secs, ending experiment")
            sock.settimeout(3600)
    
def reodering_udp_scenario():
    UDP_PORT = 6789
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', UDP_PORT))
    print("Reodering server up")
    a = struct.Struct('!II')    
    while True:
        pos = dict() # get pointer of seq to node
        tree = rbt.RedBlackTree() # store all seq in balanced tree
        print("Status: awaiting experiment")
        data, addr = sock.recvfrom(1500)
        
        if (data): # received total num packets, set up RBT to track unreceived packets
            try:
                init, total_packets = a.unpack(data)
                arr = [None]*(total_packets)
                for i in range(0,total_packets):
                    node = tree.insert(i)
                    pos[i] = node
                
                # arr[seq] = data
                print("Status: received init from", addr)
                sock.sendto("1".encode(), addr)
            except:
                continue

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,total_packets*1500)
        print("Status: experiment started")
        count = 0
        times = 0

        while True:
            try:
                data, addr = sock.recvfrom(1500)
                if (random.random() < 0.1): continue
                
                seq, checkSum, total_packets, data = network.dessemble_packet(data)

                if pos[seq]: # ack by deleting from rbt
                    node = pos[seq]
                    pos[seq] = None
                    tree.delete_obj(node)
                    ack_packet = a.pack(1, seq)
                    sock.sendto(ack_packet, addr)
                    count += 1

                    curr_min = tree.minimum()
                    if (curr_min):
                        curr_min = curr_min.item
                        #print(curr_min)
                        if (seq > curr_min): times += 1
                    
                    # if (curr_min%100==0):print(curr_min)

                if (times >= 10):
                    times = 0
                    ack_packet = a.pack(2, seq)
                    sock.sendto(ack_packet, addr)
                
                # need to decide when to check which packet not received
                # and need rbt to loop through all
                if (count == total_packets): 
                    print("Status: all packets received, ending experiment")
                    sock.settimeout(3600)
                    count = 0
                    total_packets = 0
                    break
                
            except socket.timeout as e:
                print("Status: have not received anything in 5 secs, ending experiment")
                sock.settimeout(3600)
                break
        
        r, _, _ = select.select([sock],[],[],0)
        if (r):
            data, addr = sock.recvfrom(1500)
            continue
        print("Resetting")

received_count = 0
def receiver(sock, send_mtu):
    global received_count
    global flag
    print("Status: receiver thread up")

    while True:
        try:
            data, addr = sock.recvfrom(send_mtu)
            received_count += 1
        except socket.timeout as e:
            print("Status: have not received anything in 5 secs, ending", addr)
            sock.settimeout(3600)
            flag = True
            break


def varying_mtu_udp_scenario():
    global received_count
    UDP_PORT = 7890
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', UDP_PORT))
    serverIP = socket.gethostbyname(socket.gethostname())
    a = struct.Struct('!dd')
    s = struct.Struct('!II')
    TIMEOUT = 5
    
    print("Varying mtu server up")
    mtu = None

    while not mtu:
        print("Status: awaiting next experiment")
        data, addr = sock.recvfrom(1000, socket.MSG_PEEK)

        if (data):
            data = s.unpack(data)
            send_mtu, total_packets = data[0], data[1]
            print("Status: received init from", addr)
            print("Status: settings", send_mtu, "-", total_packets)
            sock.sendto("1".encode(), addr)

        start = timer()
        print("Status: awaiting flood", addr)
        sock.settimeout(TIMEOUT)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,
                        total_packets*send_mtu)
        flag = False

        receiverThread = threading.Thread(
            target=receiver, args=(sock, send_mtu))
        receiverThread.start()
        receiverThread.join()

        end = timer()
        rtt = end - start
        percent = round((received_count/total_packets)*100, 5)
        time = round(rtt-TIMEOUT-2, 5)
        # print("Total % packets received:", percent, " - received:",
        #       received_count, "| total:", total_packets)
        # print("Total time:", time)
        # print("Status: experiment complete - ", send_mtu)

        end_packet = a.pack(time, percent)
        # print(a.unpack(end_packet))
        sock.sendto(end_packet, addr)

        logging.info('serverIP=%s|RTT=%s|received=%s|total=%s|percent=%s', serverIP, round(rtt-TIMEOUT, 5), received_count, total_packets,
                     round((received_count/total_packets)*100, 5))
        received_count = 0

    # sock.close()


def go_back_N_udp_server():
    PORT = 8000
    serverIP = socket.gethostbyname(socket.gethostname())

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    s = struct.Struct('!IHH')
    a = struct.Struct('!II')
    print("Go back N UDP Server Started")

    while True:
        print("Status: awaiting experiment")
        data, addr = sock.recvfrom(1472)

        if (data):
            init, total_packets = a.unpack(data)
            print("Status: received init from", addr)
            sock.sendto("1".encode(), addr)
        
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,total_packets*1472)
        print("Status: experiment started")
        previous_seq = -1
        count = 0
        sock.settimeout(5.0)

        while True:
            try:
                data, addr = sock.recvfrom(1500)
                if (random.random() < 0.1): continue
                # if (random.random() > 0.9): continue

                sequenceNum, checkSum, total_packets, data = network.dessemble_packet(data)
                if (sequenceNum == previous_seq + 1):
                    ack_packet = a.pack(1, sequenceNum)
                    sock.sendto(ack_packet, addr)
                    previous_seq = sequenceNum
                    count += 1

                if (count == total_packets): 
                    print("Status: all packets received, ending experiment")
                    sock.settimeout(3600)
                    count = 0
                    total_packets = 0
                    break
                
            except socket.timeout as e:
                print("Status: have not received anything in 5 secs, ending experiment")
                sock.settimeout(3600)
                break

def ll_udp_server():
    PORT = 7890
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    s = struct.Struct('!IHH')
    a = struct.Struct('!IIf')
    print("ll Server Started")
    received = set()

    while True:
        print("Status: awaiting experiment")
        try:
            data, addr = sock.recvfrom(1472)
            
            if (data):
                init, total_packets, loss = a.unpack(data)
                print("Status: received init from", addr)
                sock.sendto("1".encode(), addr)

            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,total_packets*1472)
            print("Status: experiment started")
        except Exception as e:
            print(e)

        while True:
            try:
                data, addr = sock.recvfrom(1500)
                if (random.random() < 0.1): continue
                
                sequenceNum, checkSum, total_packets, data = network.dessemble_packet(data)
                received.add(sequenceNum)
                ack_packet = a.pack(1, sequenceNum, 0)
                sock.sendto(ack_packet, addr)
                #print(len(received))
                
                if (len(received) == total_packets): 
                    print("Status: all packets received, ending experiment")
                    sock.settimeout(3600)
                    total_packets = 0
                    break
                
            except socket.timeout as e:
                print(len(received))
                print("Status: have not received anything in 5 secs, ending experiment")

                received = set()
                count = 0
                total_packets = 0   
                sock.settimeout(3600)
                break

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
        sock.settimeout(10.0)
        
        while True:
            try:
                data, addr = sock.recvfrom(1500)
                if (random.random() > 0.9): continue

                sequenceNum, checkSum, total_packets, data = network.dessemble_packet(data)
                count += 1
                ack_packet = a.pack(1, sequenceNum)
                sock.sendto(ack_packet, addr)
                # print(count)
                # if (count%1000==0): print(count)

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

import zlib
def compressed_udp_server():
    PORT = 55681
    serverIP = socket.gethostbyname(socket.gethostname())

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    s = struct.Struct('i')
    a = struct.Struct('!II')
    print("Compression Experiment Server Started")

    while True:
        print("Status: awaiting experiment")
        data, addr = sock.recvfrom(1500)

        if (data):
            init, total_packets = a.unpack(data)
            print("Status: received init from", addr)
            sock.sendto("1".encode(), addr)
        
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,total_packets*1472)
        print("Status: experiment started")
        count = 0
        sock.settimeout(5.0)
        received = list()
        count = 0

        while True:
            try:
                data, addr = sock.recvfrom(1500)
                # received.append(count)
                # count += 1
                data = zlib.decompress(data)
                sequenceNum, checkSum, total_packets, data = network.dessemble_packet(data)
                if (checkSum == network.calculate_checksum(data)): received.append(sequenceNum)
                
                if (len(received) >= total_packets):
                    sock.sendto('1'.encode(), addr)
                    print("Status: experiment ended")
                
            except Exception as e:
                print("ERROR:",e)
                print("RECEIVED:",len(received))
                sock.sendto('1'.encode(), addr)
                print("Status: experiment ended")
                break
        break
    
    # print(received[0])
    sock.close()

def congestion_udp_server():
    PORT = 7890
    serverIP = socket.gethostbyname(socket.gethostname())
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    s = struct.Struct('!IHH')
    a = struct.Struct('!IIf')
    received = set()

    print("Congestion Server Started")

    while True:
        try:    
            print("Status: awaiting experiment")
            data, addr = sock.recvfrom(1472)
            
            if (data):
                init, total_packets, lost_percent = a.unpack(data)
                print("Status: received init from", addr)
                sock.sendto("1".encode(), addr)
            
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,total_packets*1472)
            print("Status: experiment started")
            
            count = 0
            sock.settimeout(5.0)
        except Exception as e:
            print(e)

        while True:
            try:
                data, addr = sock.recvfrom(1500)
                sequenceNum, checkSum, total_packets, data = network.dessemble_packet(data)
                # random effect
                # totally lost, random
                # take longer
                # sent multiple times
                # if (network.calculate_checksum(data) != checkSum or random.random() < 0.1):
                #     if (random.randint(1, 2) == 1):
                #         continue
                #     else:
                #         error_packet = a.pack(0, sequenceNum, 0)
                #         sock.sendto(error_packet, addr)
                #     continue
                
                received.add(sequenceNum)
                # print(len(received))
                ack_packet = a.pack(1, sequenceNum, 0)
                sock.sendto(ack_packet, addr)
                
                # print(len(received))
                if (len(received) == (total_packets - 1)): 
                    print(len(received))
                    print("Status: all packets received, ending experiment")
                    sock.settimeout(3600)
                    received = set()
                    total_packets = 0
                    break
                
            except socket.timeout as e:
                print(len(received))
                print("Status: have not received anything in 5 secs, ending experiment")
                sock.settimeout(3600)
                break

if __name__ == "__main__":
    # reodering_udp_scenario()
    # varying_mtu_udp_scenario()
    # go_back_N_udp_server()
    # selective_repeat_udp_server()
    # compressed_udp_server()
    congestion_udp_server()
    # ll_udp_server()
    # selective_repeat_udp_server()
    # base_udp_scenario()
    # python udp_server.py
    # python udp.py