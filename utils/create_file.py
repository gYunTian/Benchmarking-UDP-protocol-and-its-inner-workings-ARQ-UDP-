import os
import numpy as np

#   Create file in roughly the amount of given bytes
#   Param: size, number of bytes
#
def generate_empty_file(bytes, output_path, filename):
  print("Creating file of size",bytes, "bytes")

  with open(os.path.join(output_path, filename), "wb") as out:
    out.seek(bytes * 1000000)
    out.write('a'.encode())
    print("File created at",output_path)

def generate_random_char_file(bytes, output_path, filename):
  letters = np.array(list(chr(ord('a') + i) for i in range(26)))

  with open(os.path.join(output_path, filename), "wb") as out:
    out.write(np.random.choice(letters, int((bytes * 1000 * 10000)/bytes)))
    print("File created at",output_path)

def create_file_numbers(size):

    size_bytes = size * 1024
    message = "hello world"
    with open('../data/test.txt', 'w') as f:
      repeat_amount = int((size_bytes/len(message)))
      f.write(message * repeat_amount)
    
if __name__ == "__main__":
  # generate_random_char_file(32, "../data/", "test.txt")
  create_file_numbers(32000)

