import cv2
import numpy as np
import struct
import sys

class Scanner(object):

  def __init__(self, f):
    '''
    '''
    self._pointer = 0
    self._f = f

  def jumpTo(self, where):
    '''
    '''
    self._pointer = where

  def jump(self, howmuch):
    '''
    '''
    self._pointer += howmuch

  def scanWithoutMoving(self, where, type, chunks=1):
    '''
    '''
    old_pointer = self._pointer
    self._pointer = where
    result = self.scan(type, chunks)
    self._pointer = old_pointer
    return result

  def scan(self, type, chunks=1):
    '''
    '''
    chunk_size = 1
    if type == 'uchar':
      chunk_size = 1
      symbol = 'B'
    elif type == 'ushort':
      chunk_size = 2
      symbol = 'H'
    elif type == 'uint':
      chunk_size = 4
      symbol = 'I'

    f.seek(self._pointer)
    self._pointer += chunk_size

    bytes = struct.unpack(symbol*chunks, self._f.read(chunks*chunk_size))

    if chunks == 1:
      return bytes[0]
    else:
      return bytes

filename = sys.argv[1]
width = int(sys.argv[2])
height = int(sys.argv[3])
factor = int(sys.argv[4])


import os, glob
directory = os.path.dirname(filename)
files = glob.glob(directory+'/thumbnail_*')

for filename in files:
  


  out_width = int(width/factor) + 1
  out_height = int(height/factor) + 1
  out = np.zeros((out_width, out_height), dtype=np.uint8)

  with open(filename) as f:

    s = Scanner(f)

    s.jumpTo(10)
    data_offset = s.scan('uint')

    s.jumpTo(data_offset)
    
    

    k = 0
    l = 0
    for i in range(width):
      if i % factor == 0:

        for j in range(height):
          if j % factor == 0:
            s.jumpTo(data_offset+i+j*width)

            out[k,l] = s.scan('uchar')
        
            l += 1

        l = 0
        k += 1


    cv2.imwrite('/tmp/sub_byteseeking.jpg', out)  
