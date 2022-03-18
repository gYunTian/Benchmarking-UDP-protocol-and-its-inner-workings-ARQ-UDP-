import socket, time, random
from socket import SHUT_RDWR
from utils import network

def base_tcp():
  PORT = 50000

  print("TCP server up and running")
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("", PORT))
    s.listen(1)
  
    while True:
      conn, addr = s.accept()
      # s.settimeout(5.0)   
      print(f"Connected by {addr}")
      received = set()

      try:
        count = 0
        total_packets = 21740
        start = time.time()
        while True:
          try:
            if (random.random() > 0.9): 
              # print("Skipped")
              continue
            
            data = conn.recv(1500)
            sequenceNum, checkSum, total_packets, data = network.dessemble_packet(data)
            received.add(sequenceNum)
            
            count += 1
            # print(count)
            print(len(received))
            if (len(received) == 21740):
                print("Status: all packets received")
                count = 0
                total_packets = 0
                break
          except Exception as e:
            print(len(received))
            print("ERROR:",e)
      
      finally:
        print("Status: closing conn")
        conn.shutdown(SHUT_RDWR)
        conn.close()
        
      
        

if __name__ == "__main__":
  base_tcp()
  