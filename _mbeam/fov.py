import numpy as np
import os
import sys

from constants import Constants
from tile import Tile

class FoV(object):

  def __init__(self, directory, metadata, images, file_prefix='', ratio=1):
    '''
    '''
    self._directory = directory
    self._metadata = metadata
    self._tiles = images
    self._file_prefix = file_prefix
    self._ratio = ratio

    self._tx = -1
    self._ty = -1
    self._width = -1
    self._height = -1
    # calculate these values
    self.update_bounding_box()

    self._imagedata = None

  def __str__(self):
    '''
    '''
    return 'FoV ' + self.id + ' with ' + str(len(self._tiles)) + ' tiles.'


  @property
  def id(self):
    return self._directory.strip(os.sep).split(os.sep)[-1]
    # return os.path.basename(self._directory)


  def update_bounding_box(self):
    '''
    '''
    width = -sys.maxint
    height = -sys.maxint

    minX = sys.maxint
    minY = sys.maxint
    maxX = -sys.maxint
    maxY = -sys.maxint

    for i in self._tiles:
      image = self._tiles[i]
      minX = min(minX, image._tx)
      minY = min(minY, image._ty)
      maxX = max(maxX, image._tx + image.width)
      maxY = max(maxY, image._ty + image.height)

    width = maxX - minX
    height = maxY - minY

    self._tx = minX
    self._ty = minY

    self._width = width
    self._height = height


  # def stitch(self, level=0, ratio=1):
  #   '''
  #   '''
  #   # TODO calculate ratio between one image and its' thumbnail, right now we assume 4
  #   ratio = ratio*(level+1)

  #   width = self._width / ratio
  #   height = self._height / ratio

  #   # print 'FOV',height, width, ratio

  #   out = np.zeros((height, width), dtype=np.uint8)

  #   for i in self._images:

  #     image = self._images[i]
  #     x = (image._tx - self._tx) / ratio
  #     y = (image._ty - self._ty) / ratio

  #     image = image._imagedata.levels[level].pixels
  #     # print image.shape
  #     out[y:y+image.shape[0],x:x+image.shape[1]] = image

  #   return ImageCollection(out)


  # def load_and_stitch(self, ratio=1):
  #   '''
  #   '''
  #   print 'Loading all images'
  #   # first load the thumbnails from disk
  #   for i in self._images:
  #     image = self._images[i]
  #     image.load(self._directory, self._file_prefix, self._ratio)
  #     # image.load(self._directory)

  #   # now create the pyramid
  #   stitched = self.stitch(ratio=ratio)
  #   stitched.create_full_pyramid()

  #   self._imagedata = stitched


  @staticmethod
  def from_directory(directory, file_prefix='', ratio=1):
    '''
    Loads image_coordinates.txt and metadata.txt from
    a given directory but does not load any images.

    If the directory does not seem to be a FOV or is not ready,
    return None.
    '''

    metadata_file = os.path.join(directory, Constants.METADATA_FILE)
    image_coordinates_file = os.path.join(directory, Constants.IMAGE_COORDINATES_FILE)

    # here we check if our image coordinates and metadata
    # files exist, if not we likely are not ready to parse yet
    if not os.path.exists(metadata_file) or not os.path.exists(image_coordinates_file):
      return None

    #
    # read meta data
    #
    metadata = {}

    with open(metadata_file) as f:
      for l in f.readlines():
        l = l.strip()
        values = l.split('\t')
        metadata[values[0].strip(':')] = values[-1]

    #
    # we do want to parse some of the meta data
    #
    width = int(metadata['Width'].strip('px'))
    height = int(metadata['Height'].strip('px'))
    
    #
    # index tiles
    #
    tiles = {}

    with open(image_coordinates_file) as f:
      for l in f.readlines():
        tile = Tile.from_string(l)
        # update width and height
        tile.width = width
        tile.height = height
        tiles[tile.id] = tile
        #image.load_thumbnail(directory) # load the small representation
        


    fov = FoV(directory, metadata, tiles, file_prefix, ratio)
    return fov
