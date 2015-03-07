import cv2
import numpy as np
import uuid

from cache import CACHE

class ImageData(object):

  def __init__(self, pixels):
    '''
    '''
    self._pixels = pixels

    uid = uuid.uuid4()
    self._id = uid.hex    
    CACHE[self._id] = self # here we store a pointer to the cache

  @property
  def pixels(self):

    # here we check if we have the data in memory,
    # else re-load from disk cache

    return self._pixels
