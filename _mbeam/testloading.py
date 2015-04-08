import glob
import os

from constants import Constants
from scan import Scan
from section import Section
from fov import FoV

directory = '/Users/d/Desktop/data/'

# images = glob.glob(os.path.join(directory, 'thumbnail_*.bmp'))

# loaded = []

# for i in images:

#   i = Image(i)
#   i.load(directory)
#   i._imagedata.create_full_pyramid()
#   loaded.append(i)
#   print i
#   

class Manager(object):

  def __init__(self, directory):
    '''
    '''
    self._directory = directory


  def check_path_type(self, data_path):
    '''
    Check whether the data_path is a scan, section or fov.
    '''

    # we should check how many levels deep down is the IMAGE_COORDINATES_FILE
    # level 0: this is a FOV
    # level 1: this is a section
    # level 2: this is a scan

    level = 0
    for root, dirs, files in os.walk(data_path):

      if Constants.IMAGE_COORDINATES_FILE in files:
        if level == 0:
          # this is a FoV
          return 'FOV'
        elif level == 1:
          # this is a section
          return 'SECTION'
        elif level == 2:
          # this is a scan
          return 'SCAN'

      level += 1


  def index(self, data_path):
    '''
    Sends the content listing for a given path. This detects if the path is scan, section or fov.
    '''

    views = []

    # detect if this is a scan, section or fov
    if self.check_path_type(os.path.join(self._directory, data_path)) == 'FOV':
      # this is a FoV
      fov = FoV.from_directory(os.path.join(self._directory, data_path), Constants.IMAGE_PREFIX, Constants.IMAGE_RATIO)
      self.create_tile_index_from_fov(fov)

    elif self.check_path_type(os.path.join(self._directory, data_path)) == 'SECTION':

      section = Section.from_directory(os.path.join(self._directory, data_path), Constants.IMAGE_PREFIX, Constants.IMAGE_RATIO)


    elif self.check_path_type(os.path.join(self._directory, data_path)) == 'SCAN':

      scan = Scan.from_directory(os.path.join(self._directory, data_path), Constants.IMAGE_PREFIX, Constants.IMAGE_RATIO)


  def get_normalized_tile_positions(self, fov):
    '''
    '''
    normalized_tile_positions = []

    for t in fov._tiles:
      t = fov._tiles[t]
      normalized_tx = t._tx - fov._tx
      normalized_ty = t._ty - fov._ty
      normalized_tile_positions.append([normalized_tx, normalized_ty])
      
    return normalized_tile_positions

  def create_tile



m = Manager(directory)
m.index('Alyssa/Scan1/021/000001/')
