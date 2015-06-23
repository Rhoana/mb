import numpy as np
import os
import sys
from bounding_box import BoundingBox
from tile import Tile
import cv2
import math


from util import Util
import utils

class Section(object):

  def __init__(self, json_file, calculate_bounding_box):
    '''
    '''
    self._json_file = json_file

    # Parse the json file
    self._tilespecs = utils.load_tilespecs(json_file)
    if self._tilespecs is None or len(self._tilespecs) == 0:
        raise RuntimeError, "Error while reading tilespecs file {}".format(json_file)

    # parse the tilespec and bounding box
    self._layer = self._tilespecs[0]["layer"]
    self._tiles = []
    self._bbox = BoundingBox.fromList(self._tilespecs[0]["bbox"])
    for ts in self._tilespecs:
      tile = Tile.from_dictionary(ts)
      self._tiles.append(tile)
      self._bbox.extend(tile._bbox)

    # print "section bbox: {}".format(self._bbox.toStr())

  def __str__(self):
    '''
    '''
    return 'Section ' + self.id + ' with ' + str(len(self._tiles)) + ' tiles.'


  @property
  def id(self):
    return self._layer
    

  def render(self, bbox, scale=1):
    '''
    Renders the section's given bounding box at a given scale.
    '''
    #print "Loading section {} with bbox {} and scale {}".format(self._json_file, bbox.toStr(), scale)

    # Create a canvas of the rendered image size (before downsampling)
    out_img = np.zeros((bbox.height(), bbox.width()), dtype=np.uint8)
    min_x = bbox.from_x
    min_y = bbox.from_y

    min_x = math.ceil(min_x)
    min_y = math.ceil(min_y)
    # Stitch the tiles

    # Find the relevant tiles (according to their bounding box)
    # TODO - make it faster using kdtrees or something like that
    for t in self._tiles:
      if bbox.overlap(t._bbox):

        # OLD - downsample and stitch the tiles
        # OLD - (it might be better to first stitch and then downsample, but downsampling first makes it faster)
    
        # render the tile, and put the image data in the output image
        tile_img, t_start_point = t.render()

        # print "wanted bbox: {}".format(bbox.toStr())
        # print "tile bbox: {}".format(t._bbox.toStr())
        # Compute the overlapping area of the tile in the out_img (round it to integers)
        overlap_bbox = t._bbox.intersect(bbox)
        # print "overlap bbox: {}".format(overlap_bbox.toStr())
        overlap_bbox = BoundingBox(
            math.ceil(overlap_bbox.from_x),
            math.floor(overlap_bbox.to_x),
            math.ceil(overlap_bbox.from_y),
            math.floor(overlap_bbox.to_y))
        # print "overlap bbox (rounded): {}".format(overlap_bbox.toStr())

        # crop the image that is out of the wanted bounding box
        tile_img = tile_img[
            overlap_bbox.from_y - math.ceil(t._bbox.from_y):overlap_bbox.to_y - math.ceil(t._bbox.from_y),
            overlap_bbox.from_x - math.ceil(t._bbox.from_x):overlap_bbox.to_x - math.ceil(t._bbox.from_x)
#            overlap_bbox.from_y - t._bbox.from_y:overlap_bbox.to_y - t._bbox.from_y,
#            overlap_bbox.from_x - t._bbox.from_x:overlap_bbox.to_x - t._bbox.from_x
          ]
#        print "Getting sub-image from the original at: Y={}:{}, X={}:{}".format(
#            overlap_bbox.from_y - math.ceil(t._bbox.from_y), overlap_bbox.to_y - math.ceil(t._bbox.from_y),
#            overlap_bbox.from_x - math.ceil(t._bbox.from_x), overlap_bbox.to_x - math.ceil(t._bbox.from_x))
##            overlap_bbox.from_y - t._bbox.from_y, overlap_bbox.to_y - t._bbox.from_y,
##            overlap_bbox.from_x - t._bbox.from_x, overlap_bbox.to_x - t._bbox.from_x)

        # Create a mask and an inversed mask of the tile we are going to add
        _, mask = cv2.threshold(tile_img, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        # print "mask shape: {}".format(mask.shape)

        # Set the area that is going to be changed in the output image
        roi = out_img[
            overlap_bbox.from_y - min_y:overlap_bbox.to_y - min_y,
            overlap_bbox.from_x - min_x:overlap_bbox.to_x - min_x
          ]
#        print "out-image of the output at: Y={}:{}, X={}:{}".format(
#            overlap_bbox.from_y - min_y, overlap_bbox.to_y - min_y,
#            overlap_bbox.from_x - min_x, overlap_bbox.to_x - min_x)
        # print "roi shape: {}".format(roi.shape)

        # Now black-out the area of the new image in the output image
        out_bg = cv2.bitwise_and(roi, roi, mask = mask_inv)

        # Take only the interesting stuff out of the new tile
        tile_fg = cv2.bitwise_and(tile_img, tile_img, mask = mask)

        # Put the new tile image in the main image
        dst = cv2.add(out_bg, tile_fg)
        # print "dst shape: {}".format(dst.shape)
        out_img[
#            overlap_bbox.from_y - math.ceil(min_y):overlap_bbox.from_y - math.ceil(min_y) + dst.shape[0],
#            overlap_bbox.from_x - math.ceil(min_x):overlap_bbox.from_x - math.ceil(min_x) + dst.shape[1]
            overlap_bbox.from_y - min_y:overlap_bbox.from_y - min_y + dst.shape[0],
            overlap_bbox.from_x - min_x:overlap_bbox.from_x - min_x + dst.shape[1]
          ] = dst

    # downsample the output image
    if scale > 1:
      out_img = cv2.resize(out_img, (0,0), fx=1./scale, fy=1./scale, interpolation=cv2.INTER_AREA)

    return out_img


    


  @staticmethod
  def from_file_system(json_file, calculate_bounding_box=False):
    '''
    Loads a section from a json tilespec without loading any images.
    If the json file is not a tilespec, return None.
    '''

    section = Section(json_file, calculate_bounding_box)
    return section

