import socket

# base tcp
# tls
# compression

def base_tcp():
  PORT = 50000
  s = socket.socket()
  s.bind(("", PORT))
  s.listen(5)

  print("TCP server up and running")
  while True:
    conn, address = s.accept()

    while True:
      try:
        print("Connection from:", address)
        data = conn.recv(4096)
        print("Received Data:", data)
        msg = "Reply"
        byte = msg.encode() # convert to bytes
        conn.send(byte)

      except Exception as e:
        print(e)
        break
    
    conn.close()

if __name__ == "__main__":
  base_tcp()
  