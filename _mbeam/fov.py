import numpy as np
import os
import sys

from image import Image
from imagecollection import ImageCollection

class FoV(object):

  IMAGE_COORDINATES_FILE = 'image_coordinates.txt'
  METADATA_FILE = 'metadata.txt'  
  THUMBNAIL_RATIO = 4

  def __init__(self, directory, metadata, images):
    '''
    '''
    self._directory = directory
    self._metadata = metadata
    self._images = images

    self._tx = -1
    self._ty = -1
    self._width = -1
    self._height = -1
    # calculate these values
    self.update_bounding_box()

    self._imagedata = None
    self._thumbnail = None

  def __str__(self):
    '''
    '''
    return 'FoV ' + self.id + ' with ' + str(len(self._images)) + ' images.'


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

    for i in self._images:
      image = self._images[i]
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


  def stitch_thumbnails(self, level=0):
    '''
    '''
    # TODO calculate ratio between one image and its' thumbnail, right now we assume 4
    ratio = FoV.THUMBNAIL_RATIO*(level+1)

    width = self._width / ratio
    height = self._height / ratio

    out = np.zeros((height, width), dtype=np.uint8)

    for i in self._images:

      image = self._images[i]
      x = (image._tx - self._tx) / ratio
      y = (image._ty - self._ty) / ratio

      thumb = image._thumbnail.levels[level].pixels
      out[y:y+thumb.shape[0],x:x+thumb.shape[1]] = thumb

    return ImageCollection(out)


  def load_and_stitch_thumbnails(self):
    '''
    '''
    # first load the thumbnails from disk
    for i in self._images:
      image = self._images[i]
      image.load_thumbnail(self._directory)

    # now create the pyramid
    stitched = self.stitch_thumbnails()
    stitched.create_full_pyramid()

    self._thumbnail = stitched


  @staticmethod
  def from_directory(directory):
    '''
    Loads image_coordinates.txt and metadata.txt from
    a given directory but does not load any images.

    If the directory does not seem to be a FOV or is not ready,
    return None.
    '''

    metadata_file = os.path.join(directory, FoV.METADATA_FILE)
    image_coordinates_file = os.path.join(directory, FoV.IMAGE_COORDINATES_FILE)

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
    # index images
    #
    images = {}

    with open(image_coordinates_file) as f:
      for l in f.readlines():
        image = Image.from_string(l)
        # update width and height
        image.width = width
        image.height = height
        images[image.id] = image
        #image.load_thumbnail(directory) # load the small representation
        


    fov = FoV(directory, metadata, images)
    return fov
