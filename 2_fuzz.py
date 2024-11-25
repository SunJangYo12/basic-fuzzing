import sys
import random
from pexpect import run
from pipes import quote
from subprocess import Popen,PIPE

def get_bytes(filename):
   f = open(filename, "rb").read()

   return bytearray(f)


def create_new(data):
   f = open('mutated.jpg', 'wb+')
   f.write(data)
   f.close()


def bit_flip(data):

   #optimize 25 seconds to 18 seconds
   length = len(data) - 4

   num_of_flips = int(length * .01)

   picked_indexes = []
   
   flip_array = [1,2,4,8,16,32,64,128]

   counter = 0
   while counter < num_of_flips:
      picked_indexes.append(random.choice(range(0,length)))
      counter += 1


   for x in picked_indexes:
      mask = random.choice(flip_array)
      data[x] = data[x] ^ mask

   return data


#byte flip
def magic(data):
   magic_vals = [
   (1, 255),
   (1, 255),
   (1, 127),
   (1, 0),
   (2, 255),
   (2, 0),
   (4, 255),
   (4, 0),
   (4, 128),
   (4, 64),
   (4, 127)
   ]

   picked_magic = random.choice(magic_vals)

   #print(picked_magic)

   length = len(data) - 8
   index = range(0, length)
   picked_index = random.choice(index)

   # here we are hardcoding all the byte overwrites for all of the tuples that begin (1, )
   if picked_magic[0] == 1:
      if picked_magic[1] == 255:       # 0xFF
         data[picked_index] = 255
      elif picked_magic[1] == 127:        # 0x7F
         data[picked_index] = 127
      elif picked_magic[1] == 0:       # 0x00
         data[picked_index] = 0

   # here we are hardcoding all the byte overwrites for all of the tuples that begin (2, )
   elif picked_magic[0] == 2:
      if picked_magic[1] == 255:       # 0xFFFF
         data[picked_index] = 255
         data[picked_index + 1] = 255
      elif picked_magic[1] == 0:       # 0x0000
         data[picked_index] = 0
         data[picked_index + 1] = 0

   # here we are hardcoding all of the byte overwrites for all of the tuples that being (4, )
   elif picked_magic[0] == 4:
      if picked_magic[1] == 255:       # 0xFFFFFFFF
         data[picked_index] = 255
         data[picked_index + 1] = 255
         data[picked_index + 2] = 255
         data[picked_index + 3] = 255
      elif picked_magic[1] == 0:       # 0x00000000
         data[picked_index] = 0
         data[picked_index + 1] = 0
         data[picked_index + 2] = 0
         data[picked_index + 3] = 0
      elif picked_magic[1] == 128:        # 0x80000000
         data[picked_index] = 128
         data[picked_index + 1] = 0
         data[picked_index + 2] = 0
         data[picked_index + 3] = 0
      elif picked_magic[1] == 64:         # 0x40000000
         data[picked_index] = 64
         data[picked_index + 1] = 0
         data[picked_index + 2] = 0
         data[picked_index + 3] = 0
      elif picked_magic[1] == 127:        # 0x7FFFFFFF
         data[picked_index] = 127
         data[picked_index + 1] = 255
         data[picked_index + 2] = 255
         data[picked_index + 3] = 255
      
   return data

# fuzzing
def exif(counter,data):

   #optimize 124 seconds to 25 seconds
   p = Popen(["exif", "mutated.jpg", "-verbose"], stdout=PIPE, stderr=PIPE)

   (out,err) = p.communicate()

   if p.returncode == -11:
      f = open("crashes/crash.{}.jpg".format(str(counter)), "ab+")
      f.write(data)

      print("segfault")

   if counter % 100 == 0:
      print(counter, end="\r")

   #print(out)


if len(sys.argv) < 2:
   print("Usage: JPEGfuzz.py <valid_jpg>")

else:
   filename = sys.argv[1]

   counter = 0
   while counter < 1000:
      data = get_bytes(filename)
      functions = [0, 1]

      picked_function = random.choice(functions)
      picked_function = 1
      
      if picked_function == 0:
         mutated = magic(data)
         create_new(mutated)
         exif(counter,mutated)

      else:
         mutated = bit_flip(data)
         create_new(mutated)
         exif(counter,mutated)

      counter += 1

