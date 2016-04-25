import os
import sys

from mbeam import settings


class View(object):

    def __init__(self, data_path, tx, ty, width, height, fovs, tiles, centers, luts64_map):
        '''
        '''
        self._data_path = data_path

        self._fovs = fovs
        self._tiles = tiles

        self._tx = tx
        self._ty = ty
        self._width = width
        self._height = height
        self._centers = centers
        self._luts64_map = luts64_map

    @property
    def fovs(self):
        '''
        '''
        return self._fovs

    @staticmethod
    def create(data_path, fovs, width, height, tx, ty, manager, luts64_map=None):
        '''
        '''
        # we need to probe one tile and compare it to the full-res tile
        # to get the floating point ratio in x and y between tile and full-res
        fovs[0].update_bounding_box()

        first_tile = fovs[0]._tiles[fovs[0]._tiles.keys()[0]]

        # fov paths need to be treated differently
        if manager.check_path_type(data_path) != 'FOV':
            t_abs_data_path = os.path.join(data_path, fovs[0].id)
        else:
            t_abs_data_path = data_path

        first_tile_img = first_tile.load(t_abs_data_path, settings.IMAGE_PREFIX)

        ratio_x = first_tile.width / float(first_tile_img.shape[1])
        ratio_y = first_tile.height / float(first_tile_img.shape[0])

        w_width = width / ratio_x
        w_height = height / ratio_y
        w_tx = tx / ratio_x
        w_ty = ty / ratio_y
        w_centers = []

        # now create the normalized index of all involved tiles
        tiles = {}

        for fov in fovs:
            normalized_minX = sys.maxsize
            normalized_minY = sys.maxsize
            normalized_maxX = -sys.maxsize
            normalized_maxY = -sys.maxsize

            for t in fov._tiles:

                t = fov._tiles[t]
                normalized_tx = t._tx / ratio_x - w_tx
                normalized_ty = t._ty / ratio_y - w_ty
                normalized_w = t._width / ratio_x
                normalized_h = t._height / ratio_y

                tiles[
                    fov.id +
                    t.id] = {
                    'tile': t,
                    'fov': fov.id,
                    'tx': normalized_tx,
                    'ty': normalized_ty,
                    'width': normalized_w,
                    'height': normalized_h}

                normalized_minX = min(normalized_minX, normalized_tx)
                normalized_minY = min(normalized_minY, normalized_ty)
                normalized_maxX = max(
                    normalized_maxX, normalized_tx + normalized_w)
                normalized_maxY = max(
                    normalized_maxY, normalized_ty + normalized_h)

            w_centers.append([(normalized_minX + normalized_maxX) /
                              2.0, (normalized_minY + normalized_maxY) / 2.0,
                              fov.id])

        #
        # create a new View
        #
        return View(
            data_path,
            w_tx,
            w_ty,
            w_width,
            w_height,
            fovs,
            tiles,
            w_centers,
            luts64_map)
