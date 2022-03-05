import socket
import argparse
import base64

parser = argparse.ArgumentParser(description='UDP benchmark cli')
parser.add_argument('--server', type=str, help='specify the server ip')
parser.add_argument('--port', type=str, help='specify the server port')
parser.add_argument('--file', nargs='?', type=str, help='specify the file name (if any)', default=None)
parser.add_argument('--encode', action='store_true', help='specify the file name (if any)')

args = parser.parse_args()

def process_file():
  print("JELL")
  with open("./data/video_preview_h264.mp4", "rb") as video:
    text = base64.b64decode(video.read())
    print(text)

def main():
  SERVER_IP = args.server
  SERVER_PORT = args.port 
  FILE = args.file if args.file else ""

  process_file()


  # IP_ADDR = socket.gethostbyname(socket.gethostname())
  # PORT = 3000

  # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  #   s.bind((IP_ADDR, PORT))
  #   server = (SERVER_IP, SERVER_PORT)

if __name__ == "__main__":
  main()