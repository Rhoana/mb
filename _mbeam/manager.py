import cv2
import math
import multiprocessing as mp
import numpy as np
import os
import time


from cache import CACHE
from constants import Constants
from fov import FoV
from scan import Scan
from section import Section
from view import View
from websocketcontroller import WebSocketController


class Manager(object):

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

    self._no_workers = 3#mp.cpu_count() - 1
    self._active_workers = mp.Queue(self._no_workers)

    self._tiles = {}


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

        if seconds_since_modified < Constants.FOLDER_RESTING_TIME:
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


  def get_content(self, data_path):
    '''
    Sends the content listing for a given path. This detects if the path is scan, section or fov.
    '''

    views = []

    # detect if this is a scan, section or fov
    if self.check_path_type(os.path.join(self._directory, data_path)) == 'FOV':
      # this is a FoV
      fov = FoV.from_directory(os.path.join(self._directory, data_path), Constants.IMAGE_PREFIX, Constants.IMAGE_RATIO)

      #
      # and now we create a view from it
      view = View.create(data_path, [fov], fov._width, fov._height, fov._tx, fov._ty, Constants.IMAGE_RATIO)

      views.append(view)


    elif self.check_path_type(os.path.join(self._directory, data_path)) == 'SECTION':

      section = Section.from_directory(os.path.join(self._directory, data_path), Constants.IMAGE_PREFIX, Constants.IMAGE_RATIO)

      #
      # and now we create a view from it
      # view = View.from_Section(section, 4)
      # print 'txty sec', section._tx, section._ty
      view = View.create(data_path, section._fovs, section._width, section._height, section._tx, section._ty, Constants.IMAGE_RATIO)

      views.append(view)


    elif self.check_path_type(os.path.join(self._directory, data_path)) == 'SCAN':

      scan = Scan.from_directory(os.path.join(self._directory, data_path), Constants.IMAGE_PREFIX, Constants.IMAGE_RATIO)

      for section in scan._sections:

        view = View.create(os.path.join(data_path, section.id), section._fovs, section._width, section._height, section._tx, section._ty, Constants.IMAGE_RATIO)

        views.append(view)
    
    
    view_descriptors = []

    for j,view in enumerate(views):

      #
      # we grab the width and height of the canvas of this view
      # and calculate the zoomlevels
      maxLevel = 5#len(view.canvases) - 1 ### TODO calculate
      # canvas = view.canvases[0]
      width = view._width
      height = view._height

      # zoomlevels = range(int(math.log(width / Manager.THUMBNAIL_RATIO / Manager.PYRAMID_MIN_SIZE,2)) + 1)

      view_descriptor = {}
      view_descriptor['data_path'] = view._data_path
      view_descriptor['width'] = width #/ Manager.THUMBNAIL_RATIO
      view_descriptor['height'] = height #/ Manager.THUMBNAIL_RATIO
      view_descriptor['layer'] = j
      view_descriptor['minLevel'] = 0#zoomlevels[0]
      view_descriptor['maxLevel'] = 1#maxLevel#zoomlevels[-1]
      view_descriptor['tileSize'] = Constants.CLIENT_TILE_SIZE
      view_descriptors.append(view_descriptor)

      #
      # HERE, WE ADD THE VIEW TO OUR QUEUE
      # BUT ONLY IF WE DO NOT HAVE THIS VIEW YET
      #
      if not view._data_path in self._views:
        self._viewing_queue.append(view)
        #
        # and to our views dictionary
        #
        self._views[view._data_path] = view

    return view_descriptors


  def get_image(self, data_path, x, y, z, w):
    '''
    Calculate which file(s) we need for the current openseadragon tile
    and load them as well as downsample them on the fly.
    '''

    # print '-'*80
    # print 'SD', data_path, x, y, z, w


    view = self._views[data_path]

    # calculate canvas coordinates
    x_c = x*Constants.CLIENT_TILE_SIZE
    y_c = y*Constants.CLIENT_TILE_SIZE
    w_c = Constants.CLIENT_TILE_SIZE
    h_c = Constants.CLIENT_TILE_SIZE

    top_left = [x_c, y_c]
    bottom_right = [x_c+w_c, y_c+h_c]

    # loop through all tiles and find ones which match the x_c, y_c, w_c, h_c bounding box
    required_tiles = {}
    for t in view._tiles:
      tile_dict = view._tiles[t]

      tile = tile_dict['tile']
      # now the normalized coordinates which should match the coordinate system
      tx = tile_dict['tx'] / 2**w
      ty = tile_dict['ty'] / 2**w
      width = tile_dict['width'] / 2**w
      height = tile_dict['height'] / 2**w
      t_top_left = [tx, ty]
      t_bottom_right = [tx+width, ty+height]

      comp0 = top_left[0] < t_bottom_right[0]
      comp1 = bottom_right[0] > t_top_left[0]
      comp2 = top_left[1] < t_bottom_right[1]
      comp3 = bottom_right[1] > t_top_left[1]

      overlapping = comp0 and comp1 and comp2 and comp3

      if overlapping:
        required_tiles[t] = tile_dict

    abs_data_path = os.path.join(self._directory, data_path)

    stitched = np.zeros((Constants.CLIENT_TILE_SIZE, Constants.CLIENT_TILE_SIZE), dtype=np.uint8)


    if Constants.INVERT:
      stitched[:] = 255

    # sort the required tiles to always give priority in the same order
    required_tiles_keys = sorted(required_tiles, key=lambda key: required_tiles[key])

    for t in required_tiles_keys:

      tile_dict = required_tiles[t]
      tile = tile_dict['tile']  

      # fov paths need to be treated differently
      if len(view._fovs) > 1:
        t_abs_data_path = os.path.join(abs_data_path, tile_dict['fov'])
      else:
        t_abs_data_path = abs_data_path

      #
      # NO CACHING FOR NOW
      #

      # print 'LOADING', os.path.join(t_abs_data_path, tile._filename)
      # if t in self._tiles:
      #   if w in self._tiles[t]:
      #     current_tile = self._tiles[t][w]
      #     # print 'CACHE HIT'
      #   else:
      #     # tile there but not correct zoomlevel
      #     tile.load(os.path.join(t_abs_data_path), Constants.IMAGE_PREFIX, Constants.IMAGE_RATIO)
      #     current_tile = tile.downsample(2**w)
      #     self._tiles[t][w] = tile._imagedata  
      # else: 
      tile.load(os.path.join(t_abs_data_path), Constants.IMAGE_PREFIX, Constants.IMAGE_RATIO)
      current_tile = tile.downsample(2**w)
      # self._tiles[t] = {w:current_tile}

      # stitch it in our little openseadragon tile
      tx = tile_dict['tx'] / 2**w
      ty = tile_dict['ty'] / 2**w
      t_width = tile_dict['width'] / 2**w
      t_height = tile_dict['height'] / 2**w

      stitched_x = int(max(tx, top_left[0]) - top_left[0])
      stitched_y = int(max(ty, top_left[1]) - top_left[1])

      stitched_w = min(t_width - max(top_left[0] - tx, 0), Constants.CLIENT_TILE_SIZE-stitched_x)
      stitched_h = min(t_height - max(top_left[1] - ty, 0), Constants.CLIENT_TILE_SIZE-stitched_y)

      t_sub_x = int(max(tx, top_left[0]) - tx)
      t_sub_y = int(max(ty, top_left[1]) - ty)

      stitched[stitched_y:stitched_y+stitched_h, stitched_x:stitched_x+stitched_w] = current_tile[t_sub_y:t_sub_y+stitched_h, t_sub_x:t_sub_x+stitched_w]

    if Constants.INVERT:
      stitched = 255-stitched

    return cv2.imencode('.jpg', stitched)[1].tostring()


  def tick(self):
    '''
    '''

    #
    # check for new data in the filesystem
    #
    # self.index() ### do not index all the time for now

    # #
    # # loop through cache
    # #
    # for canvas in CACHE:
    #   canvas = CACHE[canvas]
    #   delta = time.time() - canvas._last_used
    #   if (delta >= Constants.CACHE_RESTING_TIME):
    #     # we should free it here
    #     canvas.free()


    

