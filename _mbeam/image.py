import cv2
import os

from imagecollection import ImageCollection

class Image(object):

  def __init__(self, filename, tx=-1, ty=-1, tz=-1):
    '''
    '''
    self._filename = filename
    self._tx = tx
    self._ty = ty
    self._tz = tz

    self._width = -1
    self._height = -1

    self._imagedata = None

  @property
  def id(self):
    return self._filename

  @property
  def width(self):
    return self._width

  @width.setter
  def width(self, value):
    self._width = value

  @property
  def height(self):
    return self._height

  @height.setter  
  def height(self, value):
    self._height = value
  
  def load(self, directory, file_prefix='', ratio=1):
    '''
    '''
    imagedata = cv2.imread(os.path.join(directory, file_prefix + self._filename), 0) # this is grayscale loading with any OpenCV version

    self._imagedata = ImageCollection(imagedata[0:self.height/ratio, 0:self.width/ratio])

  @staticmethod
  def from_string(string, delimiter='\t'):
    '''
    Creates a new image from a string.
    '''

    string = string.strip() # remove some weird line break
    values = string.split(delimiter) # split the string

    # right now we have something like this
    # ['021_000001_003_2015-01-14T1653216213670.bmp', '2189614.003', '1853228.961', '0']
    image = Image(values[0], float(values[1]), float(values[2]), float(values[3]))
    # print values
    return image
