import math

from canvas import Canvas
from constants import Constants

class View(object):

  def __init__(self, data_path, canvases, fovs):
    '''
    '''
    self._data_path = data_path
    self._canvases = canvases
    self._fovs = fovs

  @property
  def canvases(self):
    '''
    '''
    return self._canvases

  @property
  def fovs(self):
    '''
    '''
    return self._fovs



  @staticmethod
  def create(data_path, fovs, width, height, tx, ty, ratio=1):
    '''
    '''

    zoomlevels = range(int(math.log(width / Constants.PYRAMID_MIN_SIZE, 2)) + 1)

    canvases = []

    w_width = width
    w_height = height
    w_tx = tx
    w_ty = ty

    for w in zoomlevels:

      canvases.append(Canvas(w_width, w_height, w_tx, w_ty))
      w_width /= 2
      w_height /= 2
      w_tx /= 2
      w_ty /= 2

    #
    # create a new View
    #
    return View(data_path, canvases, fovs)
    





