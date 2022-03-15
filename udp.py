import socket, sys, time, os, struct, timeit, random, threading, select
from typing import List
from utils import rbt, network
from collections import deque
from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np

# class based implementation: https://stackoverflow.com/questions/67931356/getting-connection-reset-error-on-closing-a-client-in-udp-sockets


# no frills (mass send): Done, measure and visualize
# blind resending & reodering: Do a full blast send, randomly drop, ask for resend, measure
# varying mtu: done, have to measure
# compression: done, have to measure

# reliability: GoBackN & LL based, left selective partial
#       the purpose of this is to illustrate with resending so we need compare it in scenarios with high packet drop

# (randomly drop some): 
# congestion: very slow
# custom alt to reliability: LL


def no_frills_udp_client():

    PORT = 55681
    serverIP = socket.gethostbyname(socket.gethostname())
    input_path = os.path.join('./data/', 'test.file')
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((serverIP, PORT))
    # s = struct.Struct('!IHH')
    # a = struct.Struct('!II')
    no_frills_buffer = list()
    
    with open(input_path, 'rb') as f:
        size = Path(input_path).stat().st_size
        total_packets = int(size/1472) + 1
        for i in range(0, total_packets):
            payload = f.read(1472)
            no_frills_buffer.append(payload)

    start = time.time()
    for i in range(0, len(no_frills_buffer)):
        sock.send(no_frills_buffer[i])
    
    end = time.time() - start
    print("Experiment ended")
    print("Time taken:", end)

# measure additional time taken for packet resending
# this will just mass resend

# send all those remain in rbt, by getting smallest and resending
# need a iterator that loops from smallest to largest
# then re order the packet and re assemble
def packet_resending_udp_client(MTU=1472):
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
            payload = f.read(1472)
            packet = network.create_packet(s, seq, payload, total_packets)
            sock.send(packet)
            q.append(packet) # add to double ended queue
            seq += 1

        # mass send but 
        tree = None
        pos = dict()
        arr = None
        count = 0
        while (q):
            packet = q.pop()
            seq, chk, pck, data = network.dessemble_packet(packet)

            if (not tree):  # cache packets first by constructing RBT
                arr = [None]*(pck+1)
                tree = rbt.RedBlackTree()
                for i in range(1, pck+1):
                    if (i == seq):
                        continue
                    node = tree.insert(i)
                    pos[i] = node
                arr[seq] = data

            else:  # subsequent times, if correct checksum, we remove it and put in re order array
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
        for i in range(1, len(arr)):
            if (arr[i] == None):
                print(i)
                checker += 1
        print(checker)


def varying_mtu_udp_client():
    PORT = 7890
    MTUS = [128, 256, 512, 1024, 1472, 2048, 4096, 6144, 8192, 10240]
    serverIP = socket.gethostbyname(socket.gethostname())
    input_path = os.path.join('./data/', 'test.file')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((serverIP, PORT))
    s = struct.Struct('!II')
    a = struct.Struct('!dd')

    size = Path(input_path).stat().st_size
    for mtu in MTUS:  # loop mtus
        with open(input_path, 'rb') as f:
            total_packets = int(size/mtu) + 1
            print("Experiment -", mtu, ": new experiment started")

            # we have to send a prior packet to inform mtu
            print("Experiment -", mtu, ": Sending initial")

            init_packet = s.pack(mtu, total_packets)
            sock.send(init_packet)

            # sock.sendto(mtu, (serverIP, PORT))
            print("Experiment -", mtu, ": awaiting reply for flood to begin")
            # wait for acknowledgement before start
            flag = False

            while not flag:
                data = sock.recv(mtu, socket.MSG_PEEK)
                if (data):
                    flag = True
                print("Experiment -", mtu,
                      ": received acknowledgement, beginning flood")

            time.sleep(2)
            for i in range(0, total_packets):
                # print("send",i)
                payload = f.read(mtu)
                sock.send(payload)

            print("Experiment -", mtu, ": finished transmission, awaiting results")
            results = []
            while True:
                data, addr = sock.recvfrom(mtu)
                results.append(data)
                if (len(results) == 2):
                    break

            time_taken, percent_received = a.unpack(results[-1])
            print(time_taken, percent_received)
            # while not flag:
            #     data = sock.recvfrom(mtu)
            #     if (data):
            #         print(data)
            #         flag = True

            print("Experiment -", mtu, ": received results")

        print("Experiment -", mtu, ": reset for 15s")
        time.sleep(15)


buffer = list()
time_stamp = list()
last_ack_sent = -1
in_transit = 0
var_lock = threading.Lock()

# send line: 
# ack line
# on start, mark the time
# on receive we will mark the time, and sequence number as y and x axis
# get end time
# get diff between start and end, divide into timestamps, fit each packet time into 

def go_back_N_sender(sock, total_packets, window_size, retransmission_time):
    global buffer
    global last_ack_sent
    global in_transit
    global time_stamp

    time_stamp = [None]*total_packets
    try:
        while (last_ack_sent + 1 < total_packets):
            var_lock.acquire()
            packetCount = last_ack_sent + in_transit + 1  # get current index of packet to send
            # if packets sent is less than window and index within range
            if (in_transit < window_size and packetCount < total_packets):
                sock.send(buffer[packetCount])  # send packet in current index
                time_stamp[packetCount] = time.time()  # start timer
                in_transit += 1  # increment num packets sent

            # check for timeout in earliest sent packet
            if (in_transit > 0 and time.time() - time_stamp[last_ack_sent + 1] > retransmission_time):
                # print("Sequence Number:", last_ack_sent + 1, "timed out")
                in_transit = 0  # if timed out, resend all in window

            var_lock.release()

        print("Experiment -", window_size, ": Sent all packets")
    except Exception as e:
        print("error in sender")
        print(e)

def go_back_N_receiver(sock, total_packets, a):
    global buffer
    global last_ack_sent
    global in_transit
    global time_stamp

    while (last_ack_sent + 1 < total_packets):
        if (in_transit > 0):  # if packets have been sent
            data, addr = sock.recvfrom(1472)
            data = a.unpack(data)
            ack, seq = data[0], data[1]

            var_lock.acquire()
            if (ack):  # if it is an acknowledgement for receipt of packet
                if (last_ack_sent + 1 == seq):
                    last_ack_sent += 1
                    in_transit -= 1
                else:
                    in_transit = 0
            else:  # faulty packet
                in_transit = 0
            var_lock.release()

def go_back_N_udp_client():
    global buffer
    global time_stamp
    global last_ack_sent
    global in_transit

    PORT = 7890
    serverIP = socket.gethostbyname(socket.gethostname())
    input_path = os.path.join('./data/', 'test.file')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((serverIP, PORT))
    s = struct.Struct('!IHH')
    a = struct.Struct('!II')

    for k in range(5, 10):
        print("Experiment -", k, ": new experiment started")
        with open(input_path, 'rb') as f:
            size = Path(input_path).stat().st_size
            total_packets = int(size/1472) + 1
            for i in range(0, total_packets + 1):
                payload = f.read(1472)
                buffer.append(network.create_packet(
                    s, i, payload, total_packets))

            print("Experiment -", k, ": Sending initial")
            init_rtt = time.time()
            sock.send(a.pack(1, total_packets))
            print("Experiment -", k, ": awaiting reply for flood to begin")

            TIMEOUT = 0
            while True:
                data = sock.recvfrom(1472)
                init_rtt = time.time() - init_rtt
                TIMEOUT = max(init_rtt+init_rtt+0.05, TIMEOUT)
                break
            # timeout heuristic: 2*RTT + 1*processing_time

            print("Experiment -", k,
                  ": received acknowledgement, experiment started")
            receiver_thread = threading.Thread(
                target=go_back_N_receiver, args=(sock, total_packets, a))
            sender_thread = threading.Thread(
                target=go_back_N_sender, args=(sock, total_packets, k, (0.2)))

            try:
                start = time.time()
                receiver_thread.start()
                sender_thread.start()
                receiver_thread.join()
                sender_thread.join()
            except Exception as e:
                print("Error in main")
                print(e)
                sock.close()

            print("Experiment -", k, ": complete")
            print("Experiment -", k, ":", time.time()-start)
            print("Experiment -", k, ": complete")
            print("Resetting for 20 secs")

            buffer = list()
            time_stamp = list()
            last_ack_sent = -1
            in_transit = 0

        time.sleep(20)

    sock.close()


dataPackets = []
slidingWindow = {}
isPacketTransferred = True
windowLock = threading.Lock()
def ack_receiver(clientSocket, a):
    global isPacketTransferred
    global slidingWindow
    global windowLock
    
    try:
        while len(slidingWindow) > 0 or isPacketTransferred:
            if len(slidingWindow) > 0:
                data, addr = clientSocket.recvfrom(1472)
                data = a.unpack(data)
                ack, seq = data[0], data[1]

                if (ack):
                    if seq in slidingWindow:
                        windowLock.acquire()
                        del (slidingWindow[seq])
                        if len(dataPackets) == seq + 1:
                            print("Last acknowledgement received!!")

                        windowLock.release()
    except:
        clientSocket.close()

def rdt_send(clientSocket, N, retransmissionTime, total_packets):
    global dataPackets
    global slidingWindow
    global windowLock
    global isPacketTransferred
    global dataPackets

    sentPacketNum = 0
    while sentPacketNum < total_packets:
        if N > len(slidingWindow):
            windowLock.acquire()
            slidingWindow[sentPacketNum] = time.time()

            clientSocket.send(dataPackets[sentPacketNum])
            if sentPacketNum == total_packets: isPacketTransferred = False
            windowLock.release()

            while sentPacketNum in slidingWindow:
                windowLock.acquire()
                if sentPacketNum in slidingWindow:
                    if(time.time() - slidingWindow[sentPacketNum]) > retransmissionTime:
                        print("Time out, Sequence Number = {}".format(str(sentPacketNum)))
                        slidingWindow[sentPacketNum] = time.time()
                        clientSocket.send(dataPackets[sentPacketNum])
                windowLock.release()
            sentPacketNum += 1

# this is wrong, there are two windows
# https://www.geeksforgeeks.org/sliding-window-protocol-set-3-selective-repeat/
def selective_repeat_udp_client():
    global selective_buffer
    global window
    global packet_transferred

    PORT = 7890
    serverIP = socket.gethostbyname(socket.gethostname())
    input_path = os.path.join('./data/', 'test.file')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((serverIP, PORT))
    s = struct.Struct('!IHH')
    a = struct.Struct('!II')

    for k in range(5, 10):
        print("Experiment -", k, ": new experiment started")
        with open(input_path, 'rb') as f:
            size = Path(input_path).stat().st_size
            total_packets = int(size/1472) + 1
            for i in range(0, total_packets + 1):
                payload = f.read(1472)
                buffer.append(network.create_packet(
                    s, i, payload, total_packets))

            print("Experiment -", k, ": Sending initial")
            init_rtt = time.time()
            sock.send(a.pack(1, total_packets))
            print("Experiment -", k, ": awaiting reply for flood to begin")

            TIMEOUT = 0
            while True:
                data = sock.recvfrom(1472)
                init_rtt = time.time() - init_rtt
                TIMEOUT = max(init_rtt+init_rtt+0.05, TIMEOUT)
                break
            # timeout heuristic: 2*RTT + 1*processing_time

            print("Experiment -", k,
                  ": received acknowledgement, experiment started")
            receiver_thread = threading.Thread(
                target=ack_receiver, args=(sock, a))
            sender_thread = threading.Thread(
                target=rdt_send, args=(sock, k, TIMEOUT, total_packets))

            try:
                start = time.time()
                receiver_thread.start()
                sender_thread.start()
                receiver_thread.join()
                sender_thread.join()
            except Exception as e:
                print("Error in main")
                print(e)
                sock.close()

            print("Experiment -", k, ":", time.time()-start)
            print("Experiment -", k, ": complete")
            print("Resetting for 20 secs")
        time.sleep(20)
        # break

import zlib
def compress_text():
    PORT = 55681
    serverIP = socket.gethostbyname(socket.gethostname())
    input_path = os.path.join('./data/', 'test.txt')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((serverIP, PORT))
    z = zlib.compressobj(-1,zlib.DEFLATED,31)
    s = struct.Struct('i')
    a = struct.Struct('!II')
    send_buffer = list()
    sock.settimeout(5.0)
    
    with open(input_path, 'rb') as f:
        size = Path(input_path).stat().st_size
        total_packets = int(size/1472) + 1
        start = time.time()

        for i in range(0, total_packets + 1):
            payload = f.read(1472)
            # gzip_compressed_data = zlib.compress(payload, 1)
            send_buffer.append(payload)
 
        print("Experiment sending initial")
        sock.send(a.pack(1, total_packets))
        print("Experiment awaiting reply for flood to begin")

        while True:
            data = sock.recvfrom(1472)
            break
        print("Received acknowledgement, experiment started")

        count = 0
        while count <= total_packets:
            sock.send(send_buffer[0])
            count += 1
        sock.settimeout(3600)
        while True:
            data = sock.recvfrom(1472)
            break
        end = time.time() - start
    
    print(end)
    print("Experiment complete")

    sock.close()

import utils.ll as linkedlist
POINTER_ARR = list()
LL_NUM_ACK = 0
SLIDING_WINDOW = {}
LL_LOCK = threading.Lock()
LL_BUFFER = linkedlist.dLinkedList()
WAITED = 0
STOP_THREAD = False
SEND_LIST_seq = list()
SEND_LIST_time = list()
ACK_LIST_seq = list()
ACK_list_time = list()

def ll_sender(sock, total_packets, threshold, timeout, a):
    global SLIDING_WINDOW
    global LL_LOCK
    global LL_NUM_ACK
    global WAITED
    global LL_BUFFER
    global POINTER_ARR
    global STOP_THREAD
    global SEND_LIST
    
    
    print("Total packets to send:",total_packets)
    while (LL_BUFFER.length > 0):
    # while (LL_NUM_ACK < total_packets):
        # print("STUCK1")
        # LL_LOCK.acquire()
        if (len(SLIDING_WINDOW) < threshold):
            # print("STUCK2")
            node = LL_BUFFER.get_start()
            for i in range(LL_NUM_ACK, LL_NUM_ACK+threshold+1):
                # print("STUCK3")
                if (not node.was_sent()):
                    # print("STUCK4")
                    try:
                        node.set_sent()
                        sent_time = time.time()
                        SLIDING_WINDOW[node.get_idx()] = [sent_time, 0, node] # start time, rtt, pointer
                        sock.send(node.get_data())
                        SEND_LIST_seq.append(node.get_idx())
                        SEND_LIST_time.append(sent_time)
                        node = node.get_next()

                    except Exception as e:
                        STOP_THREAD = True
                        break
            
            if (STOP_THREAD): break
        # LL_LOCK.release()
        if (STOP_THREAD): break

        # LL_LOCK.acquire()
        if (len(SLIDING_WINDOW) > 0):
            # print("STUCK7")
            for k, v in SLIDING_WINDOW.items():
                # print("STUCK8")
                sent_time, end_time, node = v
                if ((time.time() - sent_time) > 0.05):
                    # print("STUCK9")
                    sock.send(node.get_data())
                    SLIDING_WINDOW[k] = [time.time(), 0, node]
                    SEND_LIST_seq.append(k)
                    SEND_LIST_time.append(sent_time)
        # LL_LOCK.release()

        while (len(SLIDING_WINDOW) > 0):
            r, _, _ = select.select([sock],[],[],0)
            if (r):
                # print("READY TO RECEIVE")
                data, addr = sock.recvfrom(1500)
                data = a.unpack(data)
                ack, seq = data[0], data[1]

                if (seq in SLIDING_WINDOW):
                    # print("STUCK6")
                    ACK_LIST_seq.append(seq)
                    ACK_list_time.append(time.time())
                    if (seq == (LL_NUM_ACK + 1)): 
                        if (WAITED > 0):
                            LL_NUM_ACK += WAITED
                            WAITED = 0
                        else:
                            LL_NUM_ACK += 1
                    else: 
                        WAITED += 1
                    
                    del (SLIDING_WINDOW[seq])
                    LL_BUFFER.remove(POINTER_ARR[seq]) # remove pointer
                    # print(LL_BUFFER.length)
            else:
                # print("NOT READY TO RECEIVE")
                for k, v in SLIDING_WINDOW.items():
                    # print("STUCK11")
                    sent_time, end_time, node = v
                    if ((time.time() - sent_time) > 0.05):
                        # print("STUCK12")
                        sock.send(node.get_data())
                        SLIDING_WINDOW[k] = [time.time(), 0, node]
                        SEND_LIST_seq.append(k)
                        SEND_LIST_time.append(sent_time)
                    
        # print("END OF ALL")

    print("All packets sent")

def ll_receiver(sock, a, total_packets):
    global SLIDING_WINDOW
    global LL_LOCK
    global LL_BUFFER
    global POINTER_ARR
    global LL_NUM_ACK
    global WAITED
    global STOP_THREAD
    global ACK_LIST
    
    while (LL_NUM_ACK < total_packets):
        if (len(SLIDING_WINDOW) > 0):
            data, addr = sock.recvfrom(1472)
            data = a.unpack(data)
            ack, seq = data[0], data[1]

            if (ack and seq in SLIDING_WINDOW):
                ACK_LIST_seq.append(seq)
                ACK_list_time.append(time.time())
                LL_LOCK.acquire()  
                if (seq == (LL_NUM_ACK + 1)): 
                    if (WAITED > 0):
                        LL_NUM_ACK += WAITED
                        WAITED = 0
                    else:
                        LL_NUM_ACK += 2
                else: 
                    WAITED += 1
                
                del (SLIDING_WINDOW[seq])
                LL_BUFFER.remove(POINTER_ARR[seq]) # remove pointer
                LL_LOCK.release() 

            if (STOP_THREAD): break
        if (STOP_THREAD): break
    print("Received all packets")

def ll_udp_client():
    global POINTER_ARR
    global LL_BUFFER

    PORT = 7890
    serverIP = socket.gethostbyname(socket.gethostname())
    input_path = os.path.join('./data/', 'test.file')
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((serverIP, PORT))
    s = struct.Struct('!IHH')
    a = struct.Struct('!IIf')

    window_threshold = 12

    print("Experiment ll based window control started")
    with open(input_path, 'rb') as f:
        size = Path(input_path).stat().st_size

        total_packets = int(size/1472) + 1
        POINTER_ARR = [None]*(total_packets + 1)
        loss = 0.1

        for i in range(0, total_packets):
            payload = f.read(1472)
            payload = network.create_packet(s, i, payload, total_packets)
            if (isinstance(payload, (bytes))):
                node = LL_BUFFER.insert(value=payload, idx=i)
                POINTER_ARR[i] = node
            else:
                print("WDF")

        print("Experiment Sending initial")
        init_rtt = time.time()
        sock.send(a.pack(1, total_packets+1, loss))
        print("Experiment awaiting reply for flood to begin")

        TIMEOUT = 0
        while True:
            data = sock.recvfrom(1472)
            init_rtt = time.time() - init_rtt
            TIMEOUT = max(init_rtt+init_rtt+0.05, TIMEOUT)
            break

        print("Experiment ll udp received acknowledgement, experiment started")

        sender_thread = threading.Thread(
            target=ll_sender, args=(sock, total_packets, window_threshold, TIMEOUT, a))
        # receiver_thread = threading.Thread(
        #         target=ll_receiver, args=(sock, a, total_packets))

        try:
            start = time.time()
            # receiver_thread.start()
            sender_thread.start()

            # receiver_thread.join()
            sender_thread.join()
            print("Ending thread")
        except Exception as e:
            print("Error in main")
            print(e)
            sock.close()
        
        end = time.time()
        diff = end-start
        print("Experiment  complete")
        print("Experiment ", diff)
        # plt.scatter(SEND_LIST_seq, SEND_LIST_time)

        # for i in range(0,len(SEND_LIST_time)):
        #     SEND_LIST_time[i] = (end - SEND_LIST_time[i])*10
        #     try:
        #         ACK_list_time[i] = (end - ACK_list_time[i])*10
        #     except:
        #         continue
        # plt.plot(SEND_LIST_time, SEND_LIST_seq)

        plt.plot(ACK_list_time, ACK_LIST_seq)
        plt.xlabel('x - axis')
        plt.ylabel('y - axis')
        plt.savefig("test2.png")
        # print("Resetting for 20 secs")


# https://granulate.io/understanding-congestion-control/
WINDOW_SIZE = 8
SSTHRESH = 0

LAST_ACK = 0
TIME_STAMP_ARR = []

CONGESTION_AVOIDANCE = False
LOSS_EVENT = False
AVG_RTT = 0

ACKS_ARR = []
IN_TRANSIT = 0

RANDOM_ERROR = 0

congestion_lock = threading.Lock()
# https://www.cs.cmu.edu/~srini/15-441/F07/project3/project3.pdf
def congestion_receiver(sock, total_packets, a, congestion_buffer):
    global WINDOW_SIZE # cwnd
    global SSTHRESH # cap
    global IN_TRANSIT
    global LAST_ACK # ack
    global AVG_RTT # mean
    global ACKS_ARR # arr
    global LOSS_EVENT # boolean
    global MAX_RTT
    global TIME_STAMP_ARR # 0 is for timeout checks, 1 is for RTT of that packet
    global CONGESTION_AVOIDANCE

    ACKS_ARR = [0]*(total_packets+1)

    while (LAST_ACK + 1 <= total_packets): # there are still packets yet to be sent
        if (IN_TRANSIT > 0):  # if there are packets in transit
            data, addr = sock.recvfrom(1472)
            data = a.unpack(data)
            ack, seq = data[0], data[1]
            ACKS_ARR[seq] += 1 # count num of acks received for a seq

            if (ack): # valid ack
                congestion_lock.acquire()
                TIME_STAMP_ARR[seq][1] = time.time() - TIME_STAMP_ARR[seq][0] # record RTT
                print(TIME_STAMP_ARR[seq][1])

                # AVG_RTT = (AVG_RTT+TIME_STAMP_ARR[seq][1])/(LAST_ACK+1) # 
                # print(AVG_RTT)

                # if (ACKS_ARR[seq] >= 3): # latest packet received had 3 acks
                #     LOSS_EVENT = true
                #     # assume all packets after seq is lost
                #     IN_TRANSIT = 0
                #     congestion_lock.release()
                #     continue
                
                # if (not CONGESTION_AVOIDANCE): WINDOW_SIZE += 2
                # if (WINDOW_SIZE >= SSTHRESH): CONGESTION_AVOIDANCE = True
                
                if (LAST_ACK + 1 == seq):
                    LAST_ACK += 1
                    IN_TRANSIT -= 1
                else:
                    IN_TRANSIT = 0
                congestion_lock.release()

            else: # faulty packet
                congestion_lock.acquire()
                # LOSS_EVENT = true
                sock.send(congestion_buffer[seq])  # resend packet in current index
                congestion_lock.release()

def congestion_sender(sock, total_packets, retransmission_time, congestion_buffer):
    global WINDOW_SIZE
    global LAST_ACK
    global TIME_STAMP_ARR
    global RANDOM_ERROR
    global IN_TRANSIT
    global CONGESTION_AVOIDANCE
    global AVG_RTT

    TIME_STAMP_ARR = [[None,None] for i in range(0,total_packets)]
    times = 1

    sent_packets = 0
    try:
        while (sent_packets < total_packets):
            print()
            
        # while (LAST_ACK + 1 < total_packets): # still have packets to send
            
        #     packetCount = LAST_ACK + IN_TRANSIT + 1
            
        #     # if (random.random() <= RANDOM_ERROR): # simulate timeout and send
        #     #     times = random.randint(2,3)
            
        #     congestion_lock.acquire()
        #     if (IN_TRANSIT < WINDOW_SIZE and packetCount < total_packets):
        #         # for i in (0,times):
        #         sock.send(congestion_buffer[packetCount])  # send packet in current index
        #         TIME_STAMP_ARR[packetCount][0] = time.time()  # start timer
        #         IN_TRANSIT += 1  # increment num packets sent
            
        #     # if timeout resend
        #     if (IN_TRANSIT > 0 and time.time() - TIME_STAMP_ARR[LAST_ACK + 1][0] > max(retransmission_time, AVG_RTT)): 
        #         IN_TRANSIT = 0
        #         # CONGESTION_AVOIDANCE = True
            
        #     congestion_lock.release()
        print("Experiment congestion control sent all packets")

    except Exception as e:
        print(e)
        print("error in sender")

def handler():
    global CONGESTION_AVOIDANCE
    global LOSS_EVENT
    global WINDOW_SIZE
    global AVG_RTT
    global LAST_ACK

    while True:
        if (CONGESTION_AVOIDANCE):
            time.sleep(AVG_RTT)
            congestion_lock.acquire()
            WINDOW_SIZE += 1
            congestion_lock.release()

        if (LOSS_EVENT):
            congestion_lock.acquire()
            WINDOW_SIZE = max(0.5*WINDOW_SIZE, 2)
            LOSS_EVENT = False
            congestion_lock.release()

# to implement on LL
def congestion_control():
    global SSTHRESH
    global RANDOM_ERROR

    PORT = 7890
    serverIP = socket.gethostbyname(socket.gethostname())
    input_path = os.path.join('./data/', 'test.file')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((serverIP, PORT))
    s = struct.Struct('!IHH')
    a = struct.Struct('!IIf')
    congestion_buffer = list()
    
    print("Experiment congestion control started")
    with open(input_path, 'rb') as f:
        size = Path(input_path).stat().st_size
        SSTHRESH = int((size/1024)/1.5)+1

        total_packets = int(size/1472) + 1
        for i in range(0, total_packets + 1):
            payload = f.read(1472)
            congestion_buffer.append(network.create_packet(
                s, i, payload, total_packets))

        print("Experiment Sending initial")
        init_rtt = time.time()
        sock.send(a.pack(1, total_packets, RANDOM_ERROR))
        print("Experiment awaiting reply for flood to begin")

        TIMEOUT = 0
        while True:
            data = sock.recvfrom(1472)
            init_rtt = time.time() - init_rtt
            TIMEOUT = max(init_rtt+init_rtt+0.05, TIMEOUT)
            break
        # timeout heuristic: 2*RTT + 1*processing_time
        
        print("Experiment received acknowledgement, experiment started")
        receiver_thread = threading.Thread(
            target=congestion_receiver, args=(sock, total_packets, a, congestion_buffer))
        sender_thread = threading.Thread(
            target=congestion_sender, args=(sock, total_packets, TIMEOUT, congestion_buffer))
        handler_thread = threading.Thread(target=handler, args=())

        try:
            start = time.time()
            receiver_thread.start()
            sender_thread.start()
            handler_thread.start()
            receiver_thread.join()
            sender_thread.join()
            handler_thread.join()
        except Exception as e:
            print("Error in main")
            print(e)
            sock.close()
        end = time.time() - start
    print("Experiment over")
    print(end)
    time.sleep(20)



if __name__ == "__main__":
    # no_frills_udp_client()
    # varying_mtu_udp_client()
    # packet_ordering_udp_client(1472)
    # compress_text()
    # ll_udp_client()
    # selective_repeat_udp_client()
    ll_udp_client()
