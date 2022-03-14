import time, socket, struct, os, path
import threading
from utils import network
from pathlib import Path

dataPackets = []
slidingWindow = {}
isPacketTransferred = True
windowLock = threading.Lock()
buffer = list()

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

                if (ack and seq in slidingWindow):
                    windowLock.acquire()
                    del (slidingWindow[seq])
                    windowLock.release()
    except:
        clientSocket.close()

def rdt_send(clientSocket, N, retransmissionTime, total_packets):
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
            if (sentPacketNum%1000==0): print(sentPacketNum)
            sentPacketNum += 1

def selective_repeat_udp_client():
    global dataPackets
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
                dataPackets.append(network.create_packet(
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

            print("Experiment -", k, ": complete")
            print("Experiment -", k, ":", time.time()-start)
            print("Experiment -", k, ": complete")
            print("Resetting for 20 secs")
        time.sleep(20)
        # break
selective_repeat_udp_client()