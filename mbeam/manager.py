import cv2
import numpy as np
import os

from lru import LRU

from mbeam import settings
from fov import FoV
from scan import Scan
from section import Section
from util import Util
from view import View


class Manager(object):

    def __init__(self):
        '''
        '''
        self._views = LRU(50)
        # tile cache - enough for 1 MFOV for 10 parallel users
        self._tiles = LRU(61 * 10)

        self._client_tiles = {}

    def start(self):
        '''
        '''
        pass

    def check_path_type(self, data_path):
        '''
        Check whether the data_path is a scan, section or fov.
        '''

        # we should check how many levels deep is the IMAGE_COORDINATES_FILE
        # level 0: this is a FOV
        # level 1: this is a section
        # level 2: this is a scan

        if os.path.exists(
            os.path.join(
                data_path,
                settings.IMAGE_COORDINATES_FILE)):
            return 'FOV'

        if os.path.exists(
            os.path.join(
                data_path,
                Util.get_first_level_subdir(data_path),
                settings.IMAGE_COORDINATES_FILE)):
            return 'SECTION'

        if os.path.exists(
            os.path.join(
                data_path,
                Util.get_second_level_subdir(data_path),
                settings.IMAGE_COORDINATES_FILE)):
            return 'SCAN'

        return None

    def get_tree(self, data_path):
        '''
        '''

        if not data_path:
            data_path = settings.DEFAULT_DATA_FOLDER

        dir_content = sorted(Util.listdir(data_path))

        dir_listing = []

        for c in dir_content:

            full_url = os.path.join(data_path, c)

            # if not os.path.isdir(full_url):
            #   continue

            entry = {}
            entry['label'] = c
            entry['full_url'] = full_url
            entry['id'] = os.path.join(data_path, c)
            entry['load_on_demand'] = True

            dir_listing.append(entry)

        return dir_listing

    def get_content(self, data_path):
        '''
        Sends the content listing for a given path. This detects if the path is
        scan, section or fov.
        '''

        views = []

        path_type = self.check_path_type(data_path)

        # detect if this is a scan, section or fov
        if path_type == 'FOV':

            views.append({'data_path': data_path})

        elif path_type == 'SECTION':

            views.append({'data_path': data_path})

        elif path_type == 'SCAN':

            scan = Scan.from_directory(data_path, False)  # lazy indexing

            for i, section in enumerate(scan._sections):

                views.append(
                    {'data_path': os.path.join(data_path, section.id)})

        return views

    def get_meta_info(self, data_path):
        '''
        Get meta information for a requested data path.
        '''

        if data_path not in self._views.keys():

            path_type = self.check_path_type(data_path)

            # detect if this is a section or fov
            if path_type == 'FOV':
                # this is a FoV
                fov = FoV.from_directory(data_path, True)

                view = View.create(
                    data_path,
                    [fov],
                    fov._width,
                    fov._height,
                    fov._tx,
                    fov._ty,
                    self)

            elif path_type == 'SECTION':

                section = Section.from_directory(data_path, True, True)

                view = View.create(
                    data_path,
                    section._fovs,
                    section._width,
                    section._height,
                    section._tx,
                    section._ty,
                    self,
                    section._luts64_map)

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
        meta_info['tileSize'] = settings.CLIENT_TILE_SIZE
        meta_info['centers'] = view._centers

        return meta_info

    def get_image(self, data_path, x, y, z, w):
        '''
        Calculate which file(s) we need for the current openseadragon tile
        and load them as well as downsample them on the fly.
        '''

        # print '-'*80
        # print 'SD', data_path, x, y, z, w

        if settings.CACHE_CLIENT_TILES:

            osd_file_url = (data_path.replace('/', '_') + '_' + str(x) + '_' +
                            str(y) + '_' + str(z) + '_' + str(w) + '.jpg')
            osd_file_url_full = os.path.join(
                settings.CLIENT_TILE_CACHE_FOLDER, osd_file_url)

            if os.path.exists(osd_file_url_full):

                # we have this OSD tile cached on disk
                # print 'OSD CACHE HIT'
                osd_tile = cv2.imread(osd_file_url_full, 0)
                return cv2.imencode('.jpg', osd_tile)[1].tostring()

        view = self._views[data_path]

        # Create an empty dictionary for the View's luts64_map, if there isn't a map
        luts64_map = dict()
        if view._luts64_map is not None:
            luts64_map = view._luts64_map

        # calculate canvas coordinates
        x_c = x * settings.CLIENT_TILE_SIZE
        y_c = y * settings.CLIENT_TILE_SIZE
        w_c = settings.CLIENT_TILE_SIZE
        h_c = settings.CLIENT_TILE_SIZE

        top_left = [x_c, y_c]
        bottom_right = [x_c + w_c, y_c + h_c]

        # loop through all tiles and find ones which match the x_c, y_c, w_c,
        # h_c bounding box
        required_tiles = {}
        for t in view._tiles:
            tile_dict = view._tiles[t]

            tile = tile_dict['tile']
            # now the normalized coordinates which should match the coordinate
            # system
            tx = tile_dict['tx'] / 2**w
            ty = tile_dict['ty'] / 2**w
            width = tile_dict['width'] / 2**w
            height = tile_dict['height'] / 2**w
            t_top_left = [tx, ty]
            t_bottom_right = [tx + width, ty + height]

            comp0 = top_left[0] < t_bottom_right[0]
            comp1 = bottom_right[0] > t_top_left[0]
            comp2 = top_left[1] < t_bottom_right[1]
            comp3 = bottom_right[1] > t_top_left[1]

            overlapping = comp0 and comp1 and comp2 and comp3

            if overlapping:
                required_tiles[t] = tile_dict

        stitched_w = min(view._width / 2**w - x_c, settings.CLIENT_TILE_SIZE)
        stitched_h = min(view._height / 2**w - y_c, settings.CLIENT_TILE_SIZE)

        stitched = np.zeros((stitched_h, stitched_w), dtype=np.uint8)

        if settings.INVERT:
            stitched[:] = 255

        # sort the required tiles to always give priority in the same order
        required_tiles_keys = sorted(
            required_tiles, key=lambda key: required_tiles[key])

        for t in required_tiles_keys:

            tile_dict = required_tiles[t]
            tile = tile_dict['tile']

            # fov paths need to be treated differently
            if self.check_path_type(data_path) != 'FOV':
                t_abs_data_path = os.path.join(data_path, tile_dict['fov'])
            else:
                t_abs_data_path = data_path

            # print 'LOADING', os.path.join(t_abs_data_path, tile._filename)
            if t in self._tiles.keys() and w in self._tiles[t]:
                current_tile = self._tiles[t][w]
                # print 'CACHE HIT'
            else:
                #
                # we add to cache
                #
                # print "Loading lut64_map of: {} --> {}".format(tile.id, luts64_map.get(os.path.split(tile.id)[-1].lower(), None))
                tile_img = tile.load(t_abs_data_path, settings.IMAGE_PREFIX, lut_base64=luts64_map.get(os.path.split(tile.id)[-1].lower(), None))

                current_tile = Manager.downsample_image(tile_img, 2**w)
                self._tiles[t] = {w: current_tile}

            # stitch it in our little openseadragon tile
            tx = tile_dict['tx'] / 2**w
            ty = tile_dict['ty'] / 2**w
            t_width = tile_dict['width'] / 2**w
            t_height = tile_dict['height'] / 2**w

            stitched_x = int(max(tx, top_left[0]) - top_left[0])
            stitched_y = int(max(ty, top_left[1]) - top_left[1])

            stitched_w = int(
                min(t_width - max(top_left[0] - tx, 0),
                    settings.CLIENT_TILE_SIZE - stitched_x))
            stitched_h = int(
                min(t_height - max(top_left[1] - ty, 0),
                    settings.CLIENT_TILE_SIZE - stitched_y))

            t_sub_x = int(max(tx, top_left[0]) - tx)
            t_sub_y = int(max(ty, top_left[1]) - ty)

            stitched[
                stitched_y:stitched_y +
                stitched_h,
                stitched_x:stitched_x +
                stitched_w] = current_tile[
                    t_sub_y:t_sub_y +
                    stitched_h,
                    t_sub_x:t_sub_x +
                    stitched_w]

        if settings.INVERT:
            stitched = 255 - stitched

        if settings.CACHE_CLIENT_TILES:
            # print 'Writing OSD tile', osd_file_url_full
            cv2.imwrite(osd_file_url_full, stitched)

        return cv2.imencode('.jpg', stitched)[1].tostring()

    # Helping function
    @staticmethod
    def downsample_image(imagedata, factor):
        '''
        '''
        if factor == 1.:
            return imagedata

        factor = 1. / factor
        return cv2.resize(imagedata, (0, 0), fx=factor,
                          fy=factor, interpolation=cv2.INTER_LINEAR)
