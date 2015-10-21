import cv2
import glob
import math
import ntpath
import numpy as np
import os

from constants import Constants

class View(object):

  def __init__(self, data_path, tx, ty, width, height, fovs, tiles, luts):
    '''
    '''
    self._data_path = data_path
    
    self._fovs = fovs
    self._tiles = tiles
    self._luts = luts

    self._tx = tx
    self._ty = ty
    self._width = width
    self._height = height

  @property
  def fovs(self):
    '''
    '''
    return self._fovs


  @staticmethod
  def parse_LUT(lut_file):
    '''
    '''
    luts = {}
    with open(lut_file) as f:
      for l in f.readlines():
        l_splitted = l.split()
        image_file = ntpath.split(l_splitted[0])[1]
        lut = np.array([int(v) for v in l_splitted[1:257]],dtype=np.uint8)
        luts[image_file] = lut

    return luts

  @staticmethod
  def create(data_path, fovs, width, height, tx, ty, manager):
    '''
    '''
    # we need to probe one tile and compare it to the full-res tile
    # to get the floating point ratio in x and y between tile and full-res
    fovs[0].update_bounding_box()

    first_tile = fovs[0]._tiles[fovs[0]._tiles.keys()[0]]
    
    # fov paths need to be treated differently
    if manager.check_path_type(data_path) != 'FOV':
      t_abs_data_path = os.path.join(data_path, fovs[0].id)
      lut_path = glob.glob(os.path.join(data_path, '*'+Constants.LUT_FILE_SUFFIX))[0]
    else:
      t_abs_data_path = data_path
      lut_path = glob.glob(os.path.join(data_path, '..', '*'+Constants.LUT_FILE_SUFFIX))[0]

    luts = None
    if os.path.exists(lut_path):
        print 'Parsing LUT', lut_path
        luts = View.parse_LUT(lut_path)

    first_tile.load(t_abs_data_path, Constants.IMAGE_PREFIX)

    ratio_x = first_tile.width / float(first_tile._imagedata.shape[1])
    ratio_y = first_tile.height / float(first_tile._imagedata.shape[0])

    w_width = width / ratio_x
    w_height = height / ratio_y
    w_tx = tx / ratio_x
    w_ty = ty / ratio_y


    # now create the normalized index of all involved tiles
    tiles = {}

    for fov in fovs:

      for t in fov._tiles:

        t = fov._tiles[t]
        normalized_tx = t._tx / ratio_x - w_tx
        normalized_ty = t._ty / ratio_y - w_ty
        normalized_w = t._width / ratio_x
        normalized_h = t._height / ratio_y

        tiles[fov.id+t.id] = {'tile': t, 'fov':fov.id, 'fov_tx': fov._tx, 'fov_ty': fov._ty, 'tx': normalized_tx, 'ty': normalized_ty, 'width': normalized_w, 'height': normalized_h}

    #
    # create a new View
    #
    return View(data_path, w_tx, w_ty, w_width, w_height, fovs, tiles, luts)

