import numpy as np
import time
import uuid

from cache import CACHE

class ImageData(object):

  def __init__(self, pixels):
    '''
    '''
    self._pixels = pixels

    uid = uuid.uuid4()
    self._id = uid.hex
    self._last_used = time.time()
    CACHE[self._id] = self # here we store a pointer to the cache

  @property
  def pixels(self):

    # here we check if we have the data in memory,
    # else re-load from disk cache

    self._last_used = time.time()

    return self._pixels
