import os
import re
import subprocess

class Util(object):
  '''
  '''

  @staticmethod
  def listdir(path):
    '''
    '''
    # print path
    cmd = "/bin/ls {0}".format(path)

    

    ansi_escape = re.compile(r'\x1b[^m]*m')
    # ansi_escape.sub('', sometext)

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    files_list = [ansi_escape.sub('',line.strip()) for line in iter(p.stdout.readline, '')]
    # print files_list
    return files_list
