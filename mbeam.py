#!/usr/bin/env python
import os
import sys

import _mbeam

def print_help( script_name ):
  '''
  Prints help.
  '''
  description = ''
  print description
  print
  print 'Usage: ' + script_name + ' INPUT_DIRECTORY'
  print


#
# entry point
#
if __name__ == "__main__":

  # always show the help if no arguments were specified
  if len(sys.argv) != 0 and len( sys.argv ) < 2:
    print_help( sys.argv[0] )
    sys.exit( 1 )

  input_dir = sys.argv[1]

  print _mbeam.FoV.from_directory(input_dir)
