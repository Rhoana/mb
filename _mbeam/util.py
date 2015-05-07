import os
import re
import scandir
import subprocess

class Util(object):
  '''
  '''

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
