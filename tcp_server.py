import socket, time, random, os
import sys
from socket import SHUT_RDWR
from utils import network
from twisted.internet import reactor, protocol

def base_python_tcp():
  PORT = 50000
  total_packets = 21740

  print("TCP server up and running")
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("", PORT))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,total_packets*1472)
    s.listen(1)

    while True:
      try:
        conn, addr = s.accept()
        count = 0

        while True:
            data = conn.recv(10000000)
            conn.send("1".encode())

            count += 1
            if (count == total_packets):
                count = 0
                conn.shutdown(SHUT_RDWR)
                conn.close()
                break
              
      except KeyboardInterrupt:
            sys.exit()
  
class Echo(protocol.Protocol):
    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.total_packets = 21740

    def connectionMade(self):
      self._peer = self.transport.getPeer()
      self.transport.getHandle().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 21740*1472)
      print("Connected by",self._peer)

    def dataReceived(self, data):
        self.count += 1
        self.transport.write(data)
        print(self.count)
        if (self.total_packets == self.count): 
          self.count = 0
          print("All packets received")
        
    def connectionLost(self, reason):
        print("connection lost")

def main():
    print("Server started")
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(8000, factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == "__main__":
    base_python_tcp()

  