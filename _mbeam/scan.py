import numpy as np
import os
import sys


from section import Section

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
    # return os.path.basename(self._directory)

  @staticmethod
  def from_directory(directory, file_prefix='', ratio=1):
    '''
    Loads a scan from a directory without loading any images.
    '''

    sections = []

    for s in os.listdir(directory):
      section_path = os.path.join(directory, s)

      if not os.path.isdir(section_path):
        # sections always reside in directories
        continue

      section = Section.from_directory(section_path, file_prefix, ratio)
      sections.append(section)

    scan = Scan(directory, sections)
    # print section._width, section._height, section._tx, section._ty
    return scan
