import os

from fov import FoV

class Manager(object):

  def __init__(self, directory):
    '''
    '''
    self._directory = directory


  def start(self):
    '''
    '''

    for f in os.listdir(self._directory):
      f = os.path.join(self._directory, f)
      if os.path.isdir(f):
        print f
        fov = FoV.from_directory(f)
        fov.load_and_stitch_thumbnails()



  def tick(self):
    '''
    '''
    pass
    