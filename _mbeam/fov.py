import numpy as np
import os
import sys

from constants import Constants
from tile import Tile

class FoV(object):

  def __init__(self, directory, metadata, images, file_prefix='', ratio=1, calculate_bounding_box=False):
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

    if calculate_bounding_box:
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


  @staticmethod
  def filter_duplicate_lines(lines):
    '''
    from: http://stackoverflow.com/a/480227/1183453
    '''
    seen = set()
    seen_add = seen.add
    return [ x for x in lines if not (x in seen or seen_add(x))]    


  @staticmethod
  def from_directory(directory, file_prefix='', ratio=1, calculate_bounding_box=False):
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
      
      # we need to remove duplicate entries here
      lines = FoV.filter_duplicate_lines(f.readlines())
      
      for i,l in enumerate(lines):
        if i>60:
          # only look at the first 61 entries since we do not use other thumbnails
          break
        tile = Tile.from_string(l)
        # update width and height
        tile.width = width
        tile.height = height
        tiles[tile.id] = tile
        #image.load_thumbnail(directory) # load the small representation
        


    fov = FoV(directory, metadata, tiles, file_prefix, ratio, calculate_bounding_box)
    return fov
