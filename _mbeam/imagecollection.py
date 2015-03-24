import cv2
import math
import numpy as np

from constants import Constants
from imagedata import ImageData

class ImageCollection(object):

  def __init__(self, pixels):
    '''
    '''
    self._levels = range(int(math.log(pixels.shape[1]/Constants.PYRAMID_MIN_SIZE,2)) + 1)
    self._levels[0] = ImageData(pixels)

  @property
  def levels(self):
      return self._levels

  def create_next_zoomlevel(self, zoomlevel):
    '''
    '''
    pixels = self._levels[zoomlevel].pixels
    height, width = pixels.shape
    
    new_height = height / 2
    new_width = width / 2

    out = np.zeros((new_height, new_width), dtype=pixels.dtype)

    self._levels[zoomlevel+1] = ImageData(cv2.pyrDown(pixels, out))
    #self._levels[zoomlevel+1] 

  def create_full_pyramid(self):
    '''
    '''

    for i in range(len(self._levels)-1):

      self.create_next_zoomlevel(i)

      # cv2.imwrite('/tmp/zl_'+str(i)+'.jpg', self._levels[i+1].pixels)
