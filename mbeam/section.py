import os
import sys
import scandir

from mbeam import settings
from fov import FoV
from util import Util


class Section(object):

    def __init__(self, directory, fovs, calculate_bounding_box, luts64_map):
        '''
        '''
        self._directory = directory
        self._calculate_bounding_box = calculate_bounding_box

        self._fovs = fovs

        self._tx = -1
        self._ty = -1
        self._tz = -1
        self._width = -1
        self._height = -1

        if calculate_bounding_box:
            # calculate these values
            self.update_bounding_box()

        self._imagedata = None
        self._thumbnail = None

        # Either None or a mapping of a tile filename to its base64 luts string
        self._luts64_map = luts64_map

    def __str__(self):
        '''
        '''
        return 'Section ' + self.id + ' with ' + \
            str(len(self._fovs)) + ' FoVs.'

    @property
    def id(self):
        return self._directory.strip(os.sep).split(os.sep)[-1]

    def update_bounding_box(self):
        '''
        '''
        width = 0
        height = 0

        minX = sys.maxsize
        minY = sys.maxsize

        for f in self._fovs:

            offset_x = f._tx
            offset_y = f._ty

            minX = min(minX, offset_x)
            minY = min(minY, offset_y)

        for f in self._fovs:

            offset_x = f._tx
            offset_y = f._ty

            width = max(width, f._width + offset_x - minX)
            height = max(height, f._height + offset_y - minY)

        self._width = width  # - minX
        self._height = height  # - minY
        self._tx = minX
        self._ty = minY

    def index_fovs(self):
        '''
        '''
        fovs = []

        for f in Util.listdir(self._directory):
            fov_path = os.path.join(self._directory, f)

            # if not os.path.isdir(fov_path):
            #   # fovs always reside in directories
            #   continue

            fov = FoV.from_directory(fov_path, self._calculate_bounding_box)
            if fov:
                fovs.append(fov)

        self._fovs = fovs

    @staticmethod
    def from_directory(
            directory,
            calculate_bounding_box=False,
            index_subdirs=True):
        '''
        Loads a section from a directory without loading any images.

        If the directory does not seem to be a section or is not ready,
        return None.
        '''

        if index_subdirs:

            fovs = []

            for f in Util.listdir(directory):
                fov_path = os.path.join(directory, f)

                # if not os.path.isdir(fov_path):
                #   # fovs always reside in directories
                #   continue

                fov = FoV.from_directory(fov_path, calculate_bounding_box)
                if fov:
                    fovs.append(fov)

        else:

            fovs = None

        # Read the LUTS file in the directory, if one exists
        # Should either be None or a mapping of a tile filename to its base64 luts string
        luts64_map = None
        if settings.LUTS_FILE_SUFFIX is not None:
            #section_dir_name = os.path.split(directory)[-1]
            #luts_fname = os.path.join(directory, '{}{}'.format(section_dir_name, settings.LUTS_FILE_SUFFIX))
            luts_fname = ''
            # Assuming there is only a single file with that prefix, use it
            all_dir_files = scandir.scandir(directory)
            for entry in all_dir_files:
                if entry.name.endswith(settings.LUTS_FILE_SUFFIX):
                    luts_fname = os.path.join(directory, entry.name)
                    break
            if os.path.exists(luts_fname):
                # print "Using LUTS file: {}".format(luts_fname)
                data = None
                with open(luts_fname, 'r') as f:
                    data = f.readlines()
                # Map between a file name and its luts base64 string
                luts64_map = {}
                for line in data:
                    tile_full_name, b64_str = line.split('\t')
                    tile_fname = tile_full_name.split('\\')[-1].lower() # Assuming Zeiss microscope system will always stay in windows
                    b64_str = b64_str[:-2] # Remove \r\n from the end of the string
                    luts64_map[tile_fname] = b64_str
                

        section = Section(directory, fovs, calculate_bounding_box, luts64_map)
        return section
