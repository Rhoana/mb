import numpy as np
import os
import sys


from section import Section
from util import Util

class Scan(object):

  def __init__(self, directory, sections):
    '''
    '''
    self._directory = directory

    self._sections = sections


  def __str__(self):
    '''
    '''
    return 'Scan ' + self.id + ' with ' + str(len(self._sections)) + ' sections.'


  @property
  def id(self):
    return self._directory.strip(os.sep).split(os.sep)[-1]


  @staticmethod
  def from_directory(directory, calculate_bounding_box=False):
    '''
    Loads a scan from a directory without loading any images.
    '''

    sections = []

    for s in Util.listdir(directory):
      section_path = os.path.join(directory, s)

      if not os.path.isdir(section_path):
        # sections always reside in directories
        continue

      section = Section.from_directory(section_path, calculate_bounding_box)
      sections.append(section)

    scan = Scan(directory, sections)
    
    return scan
