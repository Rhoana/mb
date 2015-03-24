import numpy as np
import os
import sys


from fov import FoV
from image import Image
from imagecollection import ImageCollection

class Section(object):

  def __init__(self, directory, fovs):
    '''
    '''
    self._directory = directory

    self._fovs = fovs

    self._tx = -1
    self._ty = -1
    self._tz = -1
    self._width = -1
    self._height = -1
    # calculate these values
    self.update_bounding_box()


    self._imagedata = None
    self._thumbnail = None

  def __str__(self):
    '''
    '''
    return 'Section ' + self.id + ' with ' + str(len(self._fovs)) + ' FoVs.'


  @property
  def id(self):
    return self._directory.strip(os.sep).split(os.sep)[-1]
    # return os.path.basename(self._directory)

  def update_bounding_box(self):
    '''
    '''
    width = 0
    height = 0

    minX = sys.maxint
    minY = sys.maxint

    for f in self._fovs:

      offset_x = f._tx
      offset_y = f._ty

      minX = min(minX, offset_x)
      minY = min(minY, offset_y)


      width = max(width, f._width+offset_x)
      height = max(height, f._height+offset_y)



      # width = max(width, f._tx + f._width - minX)
      # height = max(height, f._ty + f._height - minY)

      # print 'fov', f._tx, f._ty, f._width, f._height

      # minX = min(minX, f._tx)
      # minY = min(minY, f._ty)

    #   # print 'minX', minX, minY

    #   origin = [minX, minY]
    #   translated_fov_origin = [f._tx - minX, f._ty - minY]
    #   print 'translated_fov_origin', translated_fov_origin
    #   translated_fov_width = [translated_fov_origin[0] + f._width, translated_fov_origin[1] + f._height]
    #   print 'translated_fov_width', translated_fov_width

    #   width = max(width, translated_fov_width[0])
    #   height = max(height, translated_fov_width[1])

    

    self._width = width - minX
    self._height = height - minY
    self._tx = minX
    self._ty = minY

    # print 'Width, Height', self._width, self._height
    # print 'bb',self._width, self._height, self._tx, self._ty


  def create_thumbnail(self):
    '''
    Create the empty thumbnail representation.
    '''
    ratio = FoV.THUMBNAIL_RATIO

    width = self._width / ratio
    height = self._height / ratio    

    thumbnail = ImageCollection((height, width), dtype=np.uint8)
    thumbnail.create_full_pyramid()

    self._thumbnail = thumbnail


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

  @staticmethod
  def from_directory(directory):
    '''
    Loads a section from a directory without loading any images.

    If the directory does not seem to be a section or is not ready,
    return None.
    '''

    fovs = []

    for f in os.listdir(directory):
      fov_path = os.path.join(directory, f)

      if not os.path.isdir(fov_path):
        # fovs always reside in directories
        continue

      fov = FoV.from_directory(fov_path)
      fovs.append(fov)

    section = Section(directory, fovs)
    # print section._width, section._height, section._tx, section._ty
    return section
