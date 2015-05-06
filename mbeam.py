#!/usr/bin/env python
import os
import sys

import _mbeam

CACHE = {}

#
# entry point
#
if __name__ == "__main__":

  port = 2001
  if len(sys.argv) == 2:
    port = sys.argv[1]

  manager = _mbeam.Manager()
  manager.start()

  webserver = _mbeam.WebServer(manager, port)
  webserver.start()
