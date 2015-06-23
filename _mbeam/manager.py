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
from util import Util
from view import View
from bounding_box import BoundingBox


class Manager(object):

  def __init__(self):
    '''
    '''
    self._views = {}
    self._sections = {}

    self._tiles = OrderedDict() # tile cache
    self._tile_cache_size = 61*5 # enough for 1 MFOV for 5 parallel users

    self._client_tiles = {}

  def start(self):
    '''
    '''
    pass

  def check_path_type(self, data_path):
    '''
    Check whether the data_path is a scan, or a tilespecs' section.
    '''

    # If the data_path is a file, and ends with '.json', assume that it is a tilespec
    # TODO - try to load it as json, and verify that this is a tilespec

    if data_path.endswith('.json'):
      return 'SECTION'

    # Otherwise, (the data_path is a directory) make sure that the directory contains at least a single json file
    dirs, jsons = Util.list_dirs_and_jsons(data_path)
    if len(jsons) > 0:
      return 'SCAN'

    return None

  def check_path_section(self, data_path):
    '''
    Check if the data_path is a tilespecs' section.
    '''
    # If the data_path is a file, and ends with '.json', assume that it is a tilespec
    # TODO - try to load it as json, and verify that this is a tilespec
    if data_path.endswith('.json'):
      return True

    return False

  def check_path_scan(self, data_path):
    '''
    Check if the data_path is a scan.
    (returns the tilespecs of that scan).
    '''
    # If the data_path is a not a json file (ends with '.json'), assume that it is a directory
    # and make sure that the directory contains at least a single json file
    dirs, jsons = Util.list_dirs_and_jsons(data_path)
    if len(jsons) > 0:
      # Sort the jsons by the filename
      # TODO - we should probably sort them by the layer in the tilespecs
      jsons.sort(key=lambda s: s.lower())
      return jsons

    return None



  def get_tree(self, data_path):
    '''
    '''

    if not data_path:
      data_path = Constants.DEFAULT_DATA_FOLDER

    # Get all sub directories and json files in the given directory
    dirs, jsons = Util.list_dirs_and_jsons(data_path)
    dirs = sorted(dirs)
    jsons = sorted(jsons)

    dir_listing = []

    for lst in dirs, jsons:
      for c in lst:

        full_url = os.path.join(data_path, c)

        # if not os.path.isdir(full_url):
        #   continue

        entry = {
          'label' : c,
          'full_url' : full_url,
          'id' : os.path.join(data_path, c),
          'load_on_demand' : True
        }

        dir_listing.append(entry)

    return dir_listing


  def get_content(self, data_path):
    '''
    Sends the content listing for a given path. This detects if the path is scan, section or fov.
    '''

    views = []


    # detect if this is a scan, or section
    if self.check_path_section(data_path):
      views.append({'data_path':data_path})
    else:
      jsons = self.check_path_scan(data_path)
      if jsons is not None:
        views = [{'data_path' : os.path.join(data_path, json)} for json in jsons]

    # print "get_content data_path={}, views is: {}".format(data_path, views)

    return views


  def get_meta_info(self, data_path):
    '''
    Get meta information for a requested data path.
    '''

    # print "Loading meta_info of data_path {}".format(data_path)
    section = Section.from_file_system(data_path)
    self._sections[data_path] = section

    meta_info = {}
    meta_info['layer'] = 0
    meta_info['minLevel'] = 0
    meta_info['maxLevel'] = 1
    meta_info['tileSize'] = Constants.CLIENT_TILE_SIZE

    # Make the openseadragon width and height a multiplication of a tileSize
    section_width = section._bbox.width()
    section_height = section._bbox.height()
    meta_info['width'] = math.ceil(section_width / meta_info['tileSize'] + 1) * meta_info['tileSize']
    meta_info['height'] = math.ceil(section_height / meta_info['tileSize'] + 1) * meta_info['tileSize']

    # print "meta_info is: {}".format(meta_info)

    return meta_info


#    if not data_path in self._views:
#        
#      path_type = self.check_path_type(data_path)
#
#      # detect if this is a section or fov
#      if path_type == 'FOV':
#        # this is a FoV
#        fov = FoV.from_directory(data_path, True)
#
#        width = fov._width
#        height = fov._height
#
#        view = View.create(data_path, [fov], fov._width, fov._height, fov._tx, fov._ty, self)
#
#      elif path_type == 'SECTION':
#
#        section = Section.from_directory(data_path, True, True)
#
#        width = section._width
#        height = section._height
#
#        view = View.create(data_path, section._fovs, section._width, section._height, section._tx, section._ty, self)
#
#      #
#      # and add to our views dictionary
#      #
#      self._views[data_path] = view
#
#    else:
#
#      view = self._views[data_path]
#
#    meta_info = {}
#    meta_info['width'] = view._width
#    meta_info['height'] = view._height
#    meta_info['layer'] = 0
#    meta_info['minLevel'] = 0
#    meta_info['maxLevel'] = 1
#    meta_info['tileSize'] = Constants.CLIENT_TILE_SIZE
#
#    return meta_info


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



    #view = self._views[data_path]
    if data_path not in self._sections.keys():
      section = Section.from_file_system(data_path)
      self._sections[data_path] = section
    else:
      section = self._sections[data_path]

    # calculate canvas coordinates
    x_c = x*Constants.CLIENT_TILE_SIZE
    y_c = y*Constants.CLIENT_TILE_SIZE
    w_c = Constants.CLIENT_TILE_SIZE
    h_c = Constants.CLIENT_TILE_SIZE

    # top_left = [x_c, y_c]
    # bottom_right = [x_c+w_c, y_c+h_c]

    # calculate actual data image coordinates
    real_scale = 2**w
    image_left = (x_c * real_scale) + section._bbox.from_x
    image_right = ((x_c + w_c) * real_scale) + section._bbox.from_x
    image_top = (y_c * real_scale) + section._bbox.from_y
    image_bottom = ((y_c + h_c) * real_scale) + section._bbox.from_y
    wanted_bbox = BoundingBox(image_left, image_right, image_top, image_bottom)

    # print "Rendering section {} with bbox: {}".format(data_path, wanted_bbox.toStr())
    stitched = section.render(wanted_bbox, real_scale)
    

#    # loop through all tiles and find ones which match the x_c, y_c, w_c, h_c bounding box
#    required_tiles = {}
#    for t in view._tiles:
#      tile_dict = view._tiles[t]
#
#      tile = tile_dict['tile']
#      # now the normalized coordinates which should match the coordinate system
#      tx = tile_dict['tx'] / 2**w
#      ty = tile_dict['ty'] / 2**w
#      width = tile_dict['width'] / 2**w
#      height = tile_dict['height'] / 2**w
#      t_top_left = [tx, ty]
#      t_bottom_right = [tx+width, ty+height]
#
#      comp0 = top_left[0] < t_bottom_right[0]
#      comp1 = bottom_right[0] > t_top_left[0]
#      comp2 = top_left[1] < t_bottom_right[1]
#      comp3 = bottom_right[1] > t_top_left[1]
#
#      overlapping = comp0 and comp1 and comp2 and comp3
#
#      if overlapping:
#        required_tiles[t] = tile_dict
#
#    stitched_w = min(view._width / 2**w -x_c, Constants.CLIENT_TILE_SIZE)
#    stitched_h = min(view._height / 2**w -y_c, Constants.CLIENT_TILE_SIZE)
#
#    stitched = np.zeros((stitched_h, stitched_w), dtype=np.uint8)
#
#
#    if Constants.INVERT:
#      stitched[:] = 255
#
#    # sort the required tiles to always give priority in the same order
#    required_tiles_keys = sorted(required_tiles, key=lambda key: required_tiles[key])
#
#    for t in required_tiles_keys:
#
#      tile_dict = required_tiles[t]
#      tile = tile_dict['tile']  
#
#      # fov paths need to be treated differently
#      if self.check_path_type(data_path) != 'FOV':
#        t_abs_data_path = os.path.join(data_path, tile_dict['fov'])
#      else:
#        t_abs_data_path = data_path
#
#      # print 'LOADING', os.path.join(t_abs_data_path, tile._filename)
#      if t in self._tiles:
#        if w in self._tiles[t]:
#          current_tile = self._tiles[t][w]
#          # print 'CACHE HIT'
#        else:
#          # tile there but not correct zoomlevel
#          tile.load(t_abs_data_path, Constants.IMAGE_PREFIX)
#          current_tile = tile.downsample(2**w)
#          self._tiles[t][w] = tile._imagedata  
#      else: 
#        #
#        # we add to cache
#        #
#        if len(self._tiles.keys()) >= self._tile_cache_size:
#          # delete the first added item but only if the item is not the current tile
#          first_added_item = self._tiles.keys()[0]
#
#          if t != first_added_item:
#            # print 'FREEING'
#            del self._tiles[first_added_item]
#
#        tile.load(t_abs_data_path, Constants.IMAGE_PREFIX)
#
#        current_tile = tile.downsample(2**w)
#        self._tiles[t] = {w:current_tile}
#
#      # stitch it in our little openseadragon tile
#      tx = tile_dict['tx'] / 2**w
#      ty = tile_dict['ty'] / 2**w
#      t_width = tile_dict['width'] / 2**w
#      t_height = tile_dict['height'] / 2**w
#
#      stitched_x = int(max(tx, top_left[0]) - top_left[0])
#      stitched_y = int(max(ty, top_left[1]) - top_left[1])
#
#      stitched_w = int(min(t_width - max(top_left[0] - tx, 0), Constants.CLIENT_TILE_SIZE-stitched_x))
#      stitched_h = int(min(t_height - max(top_left[1] - ty, 0), Constants.CLIENT_TILE_SIZE-stitched_y))
#
#
#      t_sub_x = int(max(tx, top_left[0]) - tx)
#      t_sub_y = int(max(ty, top_left[1]) - ty)
#
#      stitched[stitched_y:stitched_y+stitched_h, stitched_x:stitched_x+stitched_w] = current_tile[t_sub_y:t_sub_y+stitched_h, t_sub_x:t_sub_x+stitched_w]

    if Constants.INVERT:
      stitched = 255-stitched

    if Constants.CACHE_CLIENT_TILES:
      # print 'Writing OSD tile', osd_file_url_full
      cv2.imwrite(osd_file_url_full, stitched)

    # For debugging
    #osd_file_url = data_path.replace('/', '_') + '_' + str(x) + '_' + str(y) + '_' + str(z) + '_' + str(w) + '.jpg'
    #osd_file_url_full = os.path.join('/tmp/Adi/', osd_file_url)
    #cv2.imwrite(osd_file_url_full, stitched)

    return cv2.imencode('.jpg', stitched)[1].tostring()

