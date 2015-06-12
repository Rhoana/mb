import os
import re
import scandir
import subprocess

class Util(object):
  '''
  '''

  @staticmethod
  def get_first_level_subdir(path):
    '''
    '''
    return Util.subdirs(path).next()

  @staticmethod
  def get_second_level_subdir(path):
    '''
    '''
    first_sub_dir = Util.get_first_level_subdir(path)

    if first_sub_dir:
      second_sub_dir = Util.subdirs(os.path.join(path, first_sub_dir)).next()
      return os.path.join(first_sub_dir, second_sub_dir)
    return None

  @staticmethod
  def listdir(path):
    '''
    '''
    # print path


    # cmd = "/bin/ls {0}".format(path)
    # ansi_escape = re.compile(r'\x1b[^m]*m')
    # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # files_list = [ansi_escape.sub('',line.strip()) for line in iter(p.stdout.readline, '')]
    # print files_list

    files_list = list(Util.subdirs(path))

    return files_list

  @staticmethod
  def subdirs(path):
    """Yield directory names not starting with '.' under given path."""
    for entry in scandir.scandir(path):
      if not entry.name.startswith('.') and entry.is_dir():
        yield entry.name

  @staticmethod
  def list_dirs_and_jsons(path):
    '''
    '''
    # print path

    dirs = []
    jsons = []
    for entry in scandir.scandir(path):
      if entry.name.endswith('.json') and entry.is_file():
        jsons.append(entry.name)
      elif not entry.name.startswith('.') and entry.is_dir():
        dirs.append(entry.name)

    return dirs, jsons

