import cv2
import os
import numpy as np

from bounding_box import BoundingBox
from models import Transforms
from models import CombinedAffineModel

class Tile(object):

  def __init__(self, image_url, transforms, bbox):
    '''
    '''
    self._image_url = image_url
    self._transforms = transforms
    self._bbox = bbox

    self._imagedata = None

  @property
  def id(self):
    return self._image_url

  @property
  def width(self):
    return self._bbox.width()

#  @width.setter
#  def width(self, value):
#    self._width = value

  @property
  def height(self):
    return self._bbox.height()

#  @height.setter  
#  def height(self, value):
#    self._height = value
  
  def load(self):
    '''
    '''
    # print 'LOADING', self._image_url

    filename = self._image_url.replace('file://', '')
    self._imagedata = cv2.imread(filename, 0) # this is grayscale loading with any OpenCV version

  def render(self):
    '''
    Render the tile image after applying the transformations.
    Return the image data, and the starting point (top-left) coordinate of that tile.
    '''
    #if self._imagedata is not None:
    #  return self._imagedata

    # print "Rendering tile: {}".format(self._image_url)
    self.load()
    
    # Apply all transformations
    start_point = np.array([0.0, 0.0])
    combined_transform = CombinedAffineModel()
    for json_transform in self._transforms:
      # print "Parsing transformation: {}".format(json_transform)
      transform = Transforms.from_tilespec(json_transform)
      combined_transform.append(transform)
    self._image_data, start_point = combined_transform.apply_on_image(self._imagedata, start_point)
    
    return self._image_data, start_point

  def downsample(self, factor):
    '''
    '''
    if factor == 1.:
      return self._imagedata

    factor = 1./factor
    return cv2.resize(self._imagedata, (0,0), fx=factor, fy=factor, interpolation=cv2.INTER_LINEAR)


  @staticmethod
  def from_dictionary(ts):
    '''
    Creates a new tile from a tilespec dictionary.
    '''
    image_url = ts['mipmapLevels']['0']['imageUrl']
    bbox = BoundingBox.fromList(ts['bbox'])
    transforms = ts['transforms']
    
    tile = Tile(image_url, transforms, bbox)
    return tile

