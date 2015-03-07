import cv2
import numpy as np
import sys


filename = sys.argv[1]

import os, glob
directory = os.path.dirname(filename)
files = glob.glob(directory+'/thumbnail_*')

for j,filename in enumerate(files):


  width = int(sys.argv[2])
  height = int(sys.argv[3])
  factor = int(sys.argv[4])


  out_width = 512#int(width/factor) + 1
  out_height = 512#int(height/factor) + 1
  out = np.zeros((out_width, out_height), dtype=np.uint8)

  i = cv2.imread(filename)
  # o = cv2.resize(i, (out_width, out_height))
  o = cv2.pyrDown(i, out)
  cv2.imwrite('/tmp/sub_cv2_'+str(j)+'.jpg', o)
