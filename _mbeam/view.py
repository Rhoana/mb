import math
import os

from constants import Constants

class View(object):

  def __init__(self, data_path, tx, ty, width, height, fovs, tiles, ratio=1):
    '''
    '''
    self._data_path = data_path
    
    self._fovs = fovs
    self._tiles = tiles
    self._ratio = ratio

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
  def create(data_path, fovs, width, height, tx, ty, ratio=1):
    '''
    '''

    w_width = width / ratio
    w_height = height / ratio
    w_tx = tx / ratio
    w_ty = ty / ratio


    # now create the normalized index of all involved tiles
    tiles = {}

    for fov in fovs:

      for t in fov._tiles:
        t = fov._tiles[t]
        normalized_tx = t._tx / ratio - w_tx
        normalized_ty = t._ty / ratio - w_ty
        normalized_w = t._width / ratio
        normalized_h = t._height / ratio
        
        tiles[fov.id+t.id] = {'tile': t, 'fov':fov.id, 'tx': normalized_tx, 'ty': normalized_ty, 'width': normalized_w, 'height': normalized_h}

    #
    # create a new View
    #
    return View(data_path, w_tx, w_ty, w_width, w_height, fovs, tiles, ratio)
    





