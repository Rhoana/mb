import ctypes
import multiprocessing as mp
import numpy as np
import time
import uuid

from cache import CACHE
from worker import Worker

class Canvas(object):

  def __init__(self, width, height, tx=0, ty=0):
    '''
    '''
    self._width = int(width) + 1
    self._height = int(height) + 1
    self._memory = mp.RawArray(ctypes.c_ubyte, self._width*self._height)

    self._pixels = Worker.shmem_as_ndarray(self._memory)
    self._tx = tx
    self._ty = ty

    uid = uuid.uuid4()
    self._id = uid.hex
    self._last_used = time.time()
    CACHE[self._id] = self # here we store a pointer to the cache


  def place_pixels(self, pixels, tx=0, ty=0):
    '''
    '''

    # we need to subtract the offset of this Canvas due to the high numbers
    offset_x = tx - self._tx
    offset_y = ty - self._ty

    height = pixels.shape[0]
    width = pixels.shape[1]

    pixels_subarray = self.pixels[offset_y:offset_y+height, offset_x:offset_x+width]
    mask = pixels != 0
    pixels_subarray[mask] = pixels[mask]



  @property
  def pixels(self):

    # here we check if we have the data in memory,
    # else re-load from disk cache

    self._last_used = time.time()

    # we re-shape the 1D numpy array into our 2D image
    pixels = self._pixels.reshape((self._height, self._width))

    return pixels
