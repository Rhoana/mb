import math

from canvas import Canvas
from constants import Constants

class View(object):

  def __init__(self, data_path, canvases, fovs, ratio=1):
    '''
    '''
    self._data_path = data_path
    self._canvases = canvases
    self._fovs = fovs
    self._ratio = ratio

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

    zoomlevels = range(int(math.log(width / ratio / Constants.PYRAMID_MIN_SIZE, 2)) + 1)

    canvases = []

    w_width = width / ratio
    w_height = height / ratio
    w_tx = tx / ratio
    w_ty = ty / ratio

    for w in zoomlevels:

      canvases.append(Canvas(w_width, w_height, w_tx, w_ty))
      w_width /= 2
      w_height /= 2
      w_tx /= 2
      w_ty /= 2

    #
    # create a new View
    #
    return View(data_path, canvases, fovs, ratio)
    





