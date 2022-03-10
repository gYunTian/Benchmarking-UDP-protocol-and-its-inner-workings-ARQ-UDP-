import socket, time, os, struct, timeit, random, threading

from utils import rbt, network
from collections import deque
from pathlib import Path

# no frills (mass send): done
# varying mtu: partial
# compression:
# reliability (randomly drop some): partial
# tls
# congestion
# multiple parallel
# multiple conccurent access, client spawns multiple, constantly send packets, wait until exit signal
#   - server spawn thread for each,


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

# measure additional time taken for packet resending
# this will just mass resend
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

            if (not tree):  # first time we init everything
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

# packet reodering

# reassembling the packets

# do for local and cloud
# do for different file sizes
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
            
            print("Experiment -", mtu,": finished transmission, awaiting results")
            results = []
            while True:
              data, addr = sock.recvfrom(mtu)
              results.append(data)
              if (len(results) == 2): break

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
retransmission_time = 0.2
var_lock = threading.Lock()

def go_back_N_sender(sock, total_packets, window_size):
  global buffer
  global last_ack_sent
  global in_transit
  global time_stamp

  time_stamp = [None]*total_packets
  try:
    while (last_ack_sent + 1 < total_packets):
      var_lock.acquire()
      packetCount = last_ack_sent + in_transit + 1 # get current index of packet to send
      if (in_transit < window_size and packetCount < total_packets): # if packets sent is less than window and index within range
        sock.send(buffer[packetCount]) # send packet in current index
        time_stamp[packetCount] = time.time() # start timer
        in_transit += 1 # increment num packets sent
      
      if (in_transit > 0 and time.time() - time_stamp[last_ack_sent + 1] > retransmission_time): # check for timeout in earliest sent packet
        print("Sequence Number:",last_ack_sent + 1, "timed out")
        in_transit = 0 # if timed out, resend all in window
      
      var_lock.release()

    print("Sent all packets")
  except Exception as e:
    print("error in sender")
    print(e)

def go_back_N_receiver(sock, total_packets, a):
  global buffer
  global last_ack_sent
  global in_transit
  global time_stamp

  try:
    while (last_ack_sent + 1 < total_packets):
      if (in_transit > 0): # if packets have been sent
        data, addr = sock.recvfrom(1472)
        data = a.unpack(data) 
        ack, seq = data[0], data[1]

        var_lock.acquire()
        if (ack): # if it is an acknowledgement for receipt of packet
          if (last_ack_sent + 1 == seq):
            last_ack_sent += 1
            in_transit -= 1
          else: in_transit = 0
        else: # faulty packet
          in_transit = 0
        var_lock.release()
      
  except Exception as e:
    print("error in receiver")
    print(e)

def go_back_N_udp_client():

  PORT = 7890
  serverIP = socket.gethostbyname(socket.gethostname())
  input_path = os.path.join('./data/', 'test.file')

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.connect((serverIP, PORT))
  s = struct.Struct('!IHH')
  a = struct.Struct('!II')

  size = Path(input_path).stat().st_size 

  for k in range(5,10):
    with open(input_path, 'rb') as f:
      total_packets = int(size/1472) + 1

      for i in range(0, total_packets + 1):
          payload = f.read(1472)
          buffer.append(network.create_packet(s, i, payload, total_packets))
      try:
        start = time.time()
        receiver_thread = threading.Thread(target = go_back_N_receiver, args = (sock, total_packets, a))
        sender_thread = threading.Thread(target = go_back_N_sender, args = (sock, total_packets, k))
        receiver_thread.start()
        sender_thread.start()

        receiver_thread.join()
        sender_thread.join()
      except Exception as e:
        print("Error in main")
        print(e)

      print("Transfer complete: ",k)
      print("Time taken:",time.time()-start)
  
  sock.close()




if __name__ == "__main__":
    # no_frills_udp_client()
    # varying_mtu_udp_client()
    # packet_ordering_udp_client(1472)
    go_back_N_udp_client()
