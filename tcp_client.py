import os, time, socket, struct, threading, statistics as stat
import sys
from pathlib import Path
from tracemalloc import start
from utils import network
from twisted.internet import reactor, protocol, threads

def receiver(sock, total_packets):
    last_ack_sent = 0
    while (last_ack_sent + 1 < total_packets):
        data = sock.recv(1472)
        last_ack_sent += 1
        print(last_ack_sent)


def sender(sock, buffer, total_packets):
    # for i in range(0, total_packets):
    #     sock.sendall(buffer[i])
    file = open(os.path.join('./data/', 'test.file'), "r")
    data = file.read()
    sock.sendall(data.encode())
    
def base_tcp():
    PORT = 50000  # Reserve a port for your service every new transfer wants a new port or you must wait.
    serverIP = socket.gethostbyname(socket.gethostname()) # IP address of the server (current machine)
    input_path = os.path.join('./data/', 'test.file')
    cached_data = list()
    s = struct.Struct('!IHH')
    
    with open(input_path, 'rb') as f:
        size = Path(input_path).stat().st_size
        total_packets = int(size/1472) + 1

        for i in range(0, total_packets):
            payload = f.read(1472)
            cached_data.append(payload)
    
    timer = list()

    for iters in range(100):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        try:
            start = time.time()
            sock.connect((serverIP, PORT))

            receiver_thread = threading.Thread(
                target=receiver, args=(sock, total_packets))
            sender_thread = threading.Thread(
                target=sender, args=(sock, cached_data, total_packets))

            try:
                start = time.time()

                receiver_thread.start()
                sender_thread.start()
                receiver_thread.join()
                sender_thread.join()

                end = time.time() - start
                timer.append(end)
                print("Sent and received all packets/acks:",end-start)

            except Exception as e:
                print("Error in main")
                print(e)
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()

            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

            time.sleep(1)

        except KeyboardInterrupt:
            sys.exit()

        except Exception as e:
            print(e) 

        
    
    print("Time taken:",stat.mean(timer))

class EchoClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""
    def __init__(self) -> None:
        super().__init__()
        print("protocol up")

        self.ack = 0
        self.start = 0
        self.end = 0
        self.size = 0
        self.total_packets = 0
        self.buffer = []
        self.read_file(os.path.join('./data/', 'test.file'))

    def read_file(self, input_file):
        with open(input_file, 'rb') as f:
            self.size = Path(input_file).stat().st_size
            self.total_packets = int(self.size/1472) + 1
            for i in range(0, self.total_packets):
                payload = f.read(1472)
                self.buffer.append(payload)

    def connectionMade(self):
        self.transport.write(b"Connected to server")
        self.sendAllData()

    def sendAllData(self):
        print("Sending all data")
        self.start = time.time()
        for i in range(self.total_packets):
            # print("Sent:",i)
            self.transport.sendLine(self.buffer[i])
            # self.transport.write(self.buffer[i])

        self.end = time.time() - self.start
        print("Took:", self.end)

    def dataReceived(self, data):
        self.ack += 1
        # print(self.ack)

    def connectionLost(self, reason):
        print("connection lost!")

class EchoFactory(protocol.ClientFactory):    
    protocol = EchoClient
            
    def clientConnectionFailed(self, connector, reason):
        print("Connection failed!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        reactor.stop()


def main(n):
    f = EchoFactory()
    reactor.connectTCP("localhost", 8000, f)
    reactor.run()
    print("ENDED")
    


if __name__ == "__main__":
    # main(100)
    base_tcp()
