import cv2
import glob
import json
import math
import multiprocessing as mp
import numpy as np
import os
import time

from collections import OrderedDict

from constants import Constants
from fov import FoV
from scan import Scan
from section import Section
from view import View


class Manager(object):

  def __init__(self):
    '''
    '''
    self._views = {}

    self._tiles = OrderedDict() # tile cache
    self._tile_cache_size = 61*5 # enough for 1 MFOV for 5 parallel users

    self._client_tiles = {}

  def start(self):
    '''
    '''
    pass


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

      if level > 2:
        return None

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


  def fast_check_path_type(self, data_path):
    '''
    '''

    mfov_glob = glob.glob(os.path.join(data_path, Constants.IMAGE_COORDINATES_FILE))

    if len(mfov_glob) > 0:
      return 'FOV'

    first_sub_dirs = next(os.walk(data_path))[1]
    if len(first_sub_dirs) > 0:

      section_glob = glob.glob(os.path.join(data_path, first_sub_dirs[0], Constants.IMAGE_COORDINATES_FILE))

    # section_glob = glob.glob(data_path + os.sep + '*' + os.sep + Constants.IMAGE_COORDINATES_FILE)

      if len(section_glob) > 0:
        return 'SECTION'

    # scan_glob = glob.glob(data_path + os.sep + '*' + os.sep + '*' + os.sep + Constants.IMAGE_COORDINATES_FILE)    

    # if len(scan_glob) > 0:
    #   return 'SCAN'

    return None


  def get_tree(self, data_path):
    '''
    '''

    dir_content = sorted(os.listdir(data_path))

    dir_listing = []

    for c in dir_content:

      full_url = os.path.join(data_path, c)

      if not os.path.isdir(full_url):
        continue

      dir_type = self.fast_check_path_type(full_url)

      if not dir_type:
        dir_type = 'NULL'

      entry = {}
      entry['label'] = c
      entry['type'] = dir_type
      entry['full_url'] = full_url
      entry['id'] = os.path.join(data_path, c)
      entry['load_on_demand'] = True

      dir_listing.append(entry)

    return dir_listing


  def get_content(self, data_path):
    '''
    Sends the content listing for a given path. This detects if the path is scan, section or fov.
    '''

    views = []

    # detect if this is a scan, section or fov
    if self.check_path_type(data_path) == 'FOV':

      views.append({'data_path':data_path})


    elif self.check_path_type(data_path) == 'SECTION':

      views.append({'data_path':data_path})


    elif self.check_path_type(data_path) == 'SCAN':

      scan = Scan.from_directory(data_path, False) # lazy indexing

      for i, section in enumerate(scan._sections):

        views.append({'data_path':os.path.join(data_path, section.id)})

    return views


  def get_meta_info(self, data_path):
    '''
    Get meta information for a requested data path.
    '''

    if not data_path in self._views:
        
      # detect if this is a section or fov
      if self.check_path_type(data_path) == 'FOV':
        # this is a FoV
        fov = FoV.from_directory(data_path, True)

        width = fov._width
        height = fov._height

        view = View.create(data_path, [fov], fov._width, fov._height, fov._tx, fov._ty)

      elif self.check_path_type(data_path) == 'SECTION':

        section = Section.from_directory(data_path, True)

        width = section._width
        height = section._height

        view = View.create(data_path, section._fovs, section._width, section._height, section._tx, section._ty)

      #
      # and add to our views dictionary
      #
      self._views[data_path] = view

    else:

      view = self._views[data_path]

    meta_info = {}
    meta_info['width'] = view._width
    meta_info['height'] = view._height
    meta_info['layer'] = 0
    meta_info['minLevel'] = 0
    meta_info['maxLevel'] = 1
    meta_info['tileSize'] = Constants.CLIENT_TILE_SIZE

    return meta_info


  def get_image(self, data_path, x, y, z, w):
    '''
    Calculate which file(s) we need for the current openseadragon tile
    and load them as well as downsample them on the fly.
    '''

    # print '-'*80
    # print 'SD', data_path, x, y, z, w



    if Constants.CACHE_CLIENT_TILES:
      
      osd_file_url = data_path.replace('/', '_') + '_' + str(x) + '_' + str(y) + '_' + str(z) + '_' + str(w) + '.jpg'
      osd_file_url_full = os.path.join(Constants.CLIENT_TILE_CACHE_FOLDER, osd_file_url)

      if os.path.exists(osd_file_url_full):

        # we have this OSD tile cached on disk
        # print 'OSD CACHE HIT'
        osd_tile = cv2.imread(osd_file_url_full, 0)
        return cv2.imencode('.jpg', osd_tile)[1].tostring()



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

    stitched_w = min(view._width / 2**w -x_c, Constants.CLIENT_TILE_SIZE)
    stitched_h = min(view._height / 2**w -y_c, Constants.CLIENT_TILE_SIZE)

    stitched = np.zeros((stitched_h, stitched_w), dtype=np.uint8)


    if Constants.INVERT:
      stitched[:] = 255

    # sort the required tiles to always give priority in the same order
    required_tiles_keys = sorted(required_tiles, key=lambda key: required_tiles[key])

    for t in required_tiles_keys:

      tile_dict = required_tiles[t]
      tile = tile_dict['tile']  

      # fov paths need to be treated differently
      if len(view._fovs) > 1:
        t_abs_data_path = os.path.join(data_path, tile_dict['fov'])
      else:
        t_abs_data_path = data_path

      # print 'LOADING', os.path.join(t_abs_data_path, tile._filename)
      if t in self._tiles:
        if w in self._tiles[t]:
          current_tile = self._tiles[t][w]
          # print 'CACHE HIT'
        else:
          # tile there but not correct zoomlevel
          tile.load(t_abs_data_path, Constants.IMAGE_PREFIX)
          current_tile = tile.downsample(2**w)
          self._tiles[t][w] = tile._imagedata  
      else: 
        #
        # we add to cache
        #
        if len(self._tiles.keys()) >= self._tile_cache_size:
          # delete the first added item but only if the item is not the current tile
          first_added_item = self._tiles.keys()[0]

          if t != first_added_item:
            # print 'FREEING'
            del self._tiles[first_added_item]

        tile.load(t_abs_data_path, Constants.IMAGE_PREFIX)
        current_tile = tile.downsample(2**w)
        self._tiles[t] = {w:current_tile}

      # stitch it in our little openseadragon tile
      tx = tile_dict['tx'] / 2**w
      ty = tile_dict['ty'] / 2**w
      t_width = tile_dict['width'] / 2**w
      t_height = tile_dict['height'] / 2**w

      stitched_x = int(max(tx, top_left[0]) - top_left[0])
      stitched_y = int(max(ty, top_left[1]) - top_left[1])

      stitched_w = int(min(t_width - max(top_left[0] - tx, 0), Constants.CLIENT_TILE_SIZE-stitched_x))
      stitched_h = int(min(t_height - max(top_left[1] - ty, 0), Constants.CLIENT_TILE_SIZE-stitched_y))


      t_sub_x = int(max(tx, top_left[0]) - tx)
      t_sub_y = int(max(ty, top_left[1]) - ty)

      stitched[stitched_y:stitched_y+stitched_h, stitched_x:stitched_x+stitched_w] = current_tile[t_sub_y:t_sub_y+stitched_h, t_sub_x:t_sub_x+stitched_w]

    if Constants.INVERT:
      stitched = 255-stitched

    if Constants.CACHE_CLIENT_TILES:
      # print 'Writing OSD tile', osd_file_url_full
      cv2.imwrite(osd_file_url_full, stitched)

    return cv2.imencode('.jpg', stitched)[1].tostring()
