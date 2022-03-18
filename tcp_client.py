import os, time, socket, struct, pickle
from pathlib import Path
from utils import network

def base_tcp():
    PORT = 50000  # Reserve a port for your service every new transfer wants a new port or you must wait.
    serverIP = socket.gethostbyname(socket.gethostname()) # IP address of the server (current machine)
    input_path = os.path.join('./data/', 'test.file')
    cached_data = list()
    s = struct.Struct('!IHH')
    data = None

    with open(input_path, 'rb') as f:
        size = Path(input_path).stat().st_size
        total_packets = int(size/1472) + 1
        serialized_data = None

        for i in range(0, total_packets):
            payload = f.read(1472)
            # cached_data.append(payload)
            # serialized_data.append(payload)
            cached_data.append(network.create_packet(s, i, payload, total_packets))

        serialized_data = pickle.dumps(cached_data)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serverIP, PORT))
    
    print("connected, sending data")
    time.sleep(1)
    try:
        start = time.time()
        # for i in range(0, total_packets):
        #     s.sendall(cached_data[i])
        s.sendall(serialized_data)
        # s.close()
        print("TIME:",time.time() - start)
        print("Experiment ended")
        time.sleep(100)
    except: 
        # s.close()
        print("TIME:",time.time() - start)
        print("Experiment ended")
    
if __name__ == "__main__":
    base_tcp()
