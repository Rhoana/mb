import cv2
import math
import multiprocessing as mp
import os
import time


from canvas import Canvas
from drawer import Drawer
from fov import FoV
from section import Section
from view import View
from websocketcontroller import WebSocketController

class Manager(object):

  FOLDER_RESTING_TIME = 3
  CLIENT_TILE_SIZE = 512
  PYRAMID_MIN_SIZE = 256
  THUMBNAIL_RATIO = 4
  IMAGE_COORDINATES_FILE = 'image_coordinates.txt'
  FULL_IMAGE_COORDINATES_FILE = 'full_image_coordinates.txt'


  def __init__(self, directory):
    '''
    '''
    self._directory = directory
    self._data_tree = None

    self._broadcaster = None
    self._websocket_controller = WebSocketController(self)

    self._viewing_queue = []

    # self._fovs = {}
    # self._sections = {}
    self._views = {}


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
      if Manager.IMAGE_COORDINATES_FILE in files:
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


  def get_content(self, data_path):
    '''
    Sends the content listing for a given path. This detects if the path is scan, section or fov.
    '''

    views = []


    # detect if this is a scan, section or fov
    if self.check_path_type(os.path.join(self._directory, data_path)) == 'FOV':
      # this is a FoV
      fov = FoV.from_directory(os.path.join(self._directory, data_path))

      #
      # and now we create a view from it
      view = View.create([fov], fov._width / 4, fov._height / 4, fov._tx / 4, fov._ty / 4)

      views.append(view)


    elif self.check_path_type(os.path.join(self._directory, data_path)) == 'SECTION':

      section = Section.from_directory(os.path.join(self._directory, data_path))

      #
      # and now we create a view from it
      # view = View.from_Section(section, 4)
      # print 'txty sec', section._tx, section._ty
      view = View.create(section._fovs, section._width / 4, section._height / 4, section._tx / 4, section._ty / 4)

      views.append(view)

    #   # fovs = []

    #   for f in section._fovs:

    #     fov_path = os.path.join(data_path, f.id)


    #     self._fovs[fov_path] = f
    #     # fovs.append(fov)

    #   canvases.append((section._width, section._height))

    # elif self.check_path_type(os.path.join(self._directory, data_path)) == 'SCAN':
      
    #   print 'scan'



    
    
    view_descriptors = []

    for j,view in enumerate(views):

      #
      # we grab the width and height of the canvas of this view
      # and calculate the zoomlevels
      maxLevel = len(view.canvases) - 1
      canvas = view.canvases[0]
      width = canvas._width
      height = canvas._height

      # zoomlevels = range(int(math.log(width / Manager.THUMBNAIL_RATIO / Manager.PYRAMID_MIN_SIZE,2)) + 1)

      view_descriptor = {}
      view_descriptor['width'] = width #/ Manager.THUMBNAIL_RATIO
      view_descriptor['height'] = height #/ Manager.THUMBNAIL_RATIO
      view_descriptor['layer'] = j
      view_descriptor['minLevel'] = 0#zoomlevels[0]
      view_descriptor['maxLevel'] = maxLevel#zoomlevels[-1]
      view_descriptor['tileSize'] = Manager.CLIENT_TILE_SIZE
      view_descriptors.append(view_descriptor)

      #
      # HERE, WE ADD THE VIEW TO OUR QUEUE
      # BUT ONLY IF WE DO NOT HAVE THIS VIEW YET
      #
      if not data_path in self._views:
        self._viewing_queue.append(view)
        #
        # and to our views dictionary
        #
        self._views[data_path] = view

    return view_descriptors


  def get_image(self, data_path, x, y, z, w):
    '''
    '''

    image = self._views[data_path].canvases[w].pixels
    ts = Manager.CLIENT_TILE_SIZE
    # print image, image.shape

    return cv2.imencode('.jpg', image[y*ts:y*ts+ts,x*ts:x*ts+ts])[1].tostring()


  def tick(self):
    '''
    '''

    if len(self._viewing_queue) != 0:
      view = self._viewing_queue.pop(0)

      # we now use a separate process to work on this view
      args = (self, view)
      worker = mp.Process(target=Drawer.run, args=args)
      # self._active_workers.put(1) # increase worker counter
      print 'starting drawer', view
      worker.start()


    #
    # check for new data in the filesystem
    #
    self.index()


