import cv2
import math
import os
import time


from fov import FoV
from websocketcontroller import WebSocketController

class Manager(object):

  FOLDER_RESTING_TIME = 3
  CLIENT_TILE_SIZE = 512

  def __init__(self, directory):
    '''
    '''
    self._directory = directory
    self._data_tree = None

    self._broadcaster = None
    self._websocket_controller = WebSocketController(self)

    self._fovs = {}


  def start(self):
    '''
    '''

    # for f in os.listdir(self._directory):
    #   f = os.path.join(self._directory, f)
    #   if os.path.isdir(f):
    #     print f
    #     fov = FoV.from_directory(f)
    #     fov.load_and_stitch_thumbnails()
    

  def index(self):
    '''
    '''

    data_tree = {}
    rootdir = self._directory
    start = rootdir.rfind(os.sep) + 1
    # rootdir = self._directory.rstrip(os.sep)
    # start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
      folders = path[start:].split(os.sep)

      # print folders
      subdir = {}
      if folders[0] != '':
        folder_path = os.path.join(rootdir, os.sep.join(folders))

        seconds_since_modified = time.time() - os.path.getmtime(folder_path)

        if seconds_since_modified < Manager.FOLDER_RESTING_TIME:
          # this folder shall not be indexed yet
          # we need to jump out
          return False
        
        parent = reduce(dict.get, folders[:-1], data_tree)
        parent[folders[-1]] = subdir

    new_data = False
    if data_tree != self._data_tree:
      new_data = True

    self._data_tree = data_tree

    if new_data:
      # new data arrived, notify clients
      self._websocket_controller.send_data_tree()
    

  def get_content(self, data_path):
    '''
    Sends the content listing for a given path. This detects if the path is scan, section or fov.
    '''
    # right now assume, it is a FOV
    fov = FoV.from_directory(os.path.join(self._directory, data_path))

    if not data_path in self._fovs:
      self._fovs[data_path] = fov

    fovs = [fov]

    zoomlevels = range(int(math.log(fov._width/512,2)) + 1)

    descriptors = []

    # sections = []
    for i,s in enumerate(fovs):
      fov_descriptor = {}
      fov_descriptor['width'] = fov._width / 4
      fov_descriptor['height'] = fov._height / 4 
      fov_descriptor['layer'] = i
      fov_descriptor['minLevel'] = zoomlevels[0]
      fov_descriptor['maxLevel'] = zoomlevels[-1]
      fov_descriptor['tileSize'] = Manager.CLIENT_TILE_SIZE
      descriptors.append(fov_descriptor)

    print descriptors

    return descriptors


  def get_image(self, data_path, x, y, z, level):
    '''
    '''

    fov = self._fovs[data_path]

    if not fov._thumbnail:
      print 'stitching'
      fov.load_and_stitch_thumbnails()

    ts = Manager.CLIENT_TILE_SIZE

    image = fov._thumbnail._levels[level]._pixels
    print image.shape
    # cv2.imwrite('/tmp/cv2.jpg', image)
    return cv2.imencode('.jpg', image[y*ts:y*ts+ts,x*ts:x*ts+ts])[1].tostring()


  def tick(self):
    '''
    '''
    self.index()
