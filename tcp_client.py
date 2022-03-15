import os, time, socket
from pathlib import Path

def base_tcp():
    PORT = 50000  # Reserve a port for your service every new transfer wants a new port or you must wait.
    serverIP = socket.gethostbyname(socket.gethostname()) # IP address of the server (current machine)
    input_path = os.path.join('./data/', 'test.file')
    cached_data = list()

    with open(input_path, 'rb') as f:
        size = Path(input_path).stat().st_size
        total_packets = int(size/1472) + 1
        for i in range(0, total_packets):
            payload = f.read(1472)
            cached_data.append(payload)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serverIP, PORT))

    try:
        start = time.time()
        for i in range(0, total_packets):
            # print(i)
            s.send(cached_data[i])
        s.close()
        
        print("TIME:",time.time() - start)
        print("Experiment ended")
    except: 
        s.close()
        print("TIME:",time.time() - start)
        print("Experiment ended")
    
if __name__ == "__main__":
    base_tcp()
