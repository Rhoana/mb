import cv2
import glob
import os
import base64
import struct

# The LUT decode format (from packed base64)
DECODE_FORMAT = ''.join(['B'] * 256)

class Tile(object):

    def __init__(self, filename, tx=-1, ty=-1, tz=-1):
        '''
        '''
        self._filename = filename
        self._basename = os.path.splitext(self._filename)[0]
        self._tx = tx
        self._ty = ty
        self._tz = tz

        self._width = -1
        self._height = -1

        self._imagedata = None

    @property
    def id(self):
        return self._filename

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    def load(self, directory, file_prefix='', ratio_x=1, ratio_y=1, lut_base64=None):
        '''
        '''

        file_path = os.path.join(directory, file_prefix + self._basename)
        file = glob.glob(file_path + '.*')[0]

        # this is grayscale loading with any OpenCV version
        imagedata = cv2.imread(file, 0)

        # Apply the look up table of the tile
        if lut_base64 is not None:
            lut = struct.unpack(DECODE_FORMAT, base64.b64decode(lut_base64))
            imagedata = cv2.LUT(imagedata, lut)
        return imagedata

    @staticmethod
    def from_string(string):
        '''
        Creates a new image from a string.
        '''

        string = string.strip()  # remove some weird line break
        values = string.split()  # split the string

        # right now we have something like this
        # ['021_000001_003_2015-01-14T1653216213670.bmp', '2189614.003',
        #  '1853228.961', '0']

        tile = Tile(
            values[0], float(
                values[1]), float(
                values[2]), float(
                values[3]))
        # print values
        return tile
