import socket, time, random
from socket import SHUT_RDWR


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

      try:
        count = 0
        total_packets = 21740
        while True:
          try:
            if (random.random() > 0.9): continue
            data = conn.recv(1500)
            count += 1
            if (count == 21740):
                print("Status: all packets received")
                count = 0
                total_packets = 0
                break
          except Exception as e:
            print(e)
      
      finally:
        print("Status: closing conn")
        conn.shutdown(SHUT_RDWR)
        conn.close()
        
      
        

if __name__ == "__main__":
  base_tcp()
  