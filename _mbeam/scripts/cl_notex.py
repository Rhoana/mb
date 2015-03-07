import pyopencl as cl
import numpy as np
import cv2 # OpenCV 2.3.1
import sys


from powertrain import Powertrain

filename = sys.argv[1]
width = int(sys.argv[2])
height = int(sys.argv[3])
factor = int(sys.argv[4])



# setup transform kernel
loader = Powertrain(True)
loader.program = """
  __kernel void ds(__global const uchar *img_g,
                   const int width,
                   const int height,
                   const int out_width,
                   const int out_height,                 
                   __global uchar *out_g) {
    int gid = get_global_id(0);

    int col = gid % width;
    int row = gid / width;

    if ((col >= width) || (row >= height)) {
      return;
    }  


    if (col < 0) {
      return;
    }

    int new_row = row/2;
    int new_col = col/2;

    if ((new_col >= out_width) || (new_row >= out_height)) {
      return;
    }

    if (new_col < 0) {
      return;
    }  

    int k = new_row*out_width + new_col;

    if (row % 2 == 0 && col % 2 == 0) {

      uchar c = img_g[gid];
      uchar r = img_g[gid+1];
      uchar b = img_g[gid+width];
      uchar b_r = img_g[gid+width+1];

      uchar val = (c + r + b + b_r) / 4;

      //out_g[k] = img_g[gid];
      out_g[k] = val;
    }
  }

"""


output_width = int(width/factor) + 1
output_height = int(height/factor) + 1



filename = sys.argv[1]

import os, glob
directory = os.path.dirname(filename)
files = glob.glob(directory+'/thumbnail_*')

for filename in files:
    


  # load a 512x512 image
  Img = cv2.imread(filename, cv2.CV_LOAD_IMAGE_GRAYSCALE)

  OutImg = np.empty(shape=(output_width, output_height), dtype=np.uint8)



  mf = cl.mem_flags
  in_img = cl.Buffer(loader.context, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=Img)


  out_img = cl.Buffer(loader.context, mf.WRITE_ONLY, OutImg.nbytes)



  loader.program.ds(loader. queue,
                    (width*height,),
                    None,
                    in_img,
                    np.int32(width),
                    np.int32(height),
                    np.int32(output_width),
                    np.int32(output_height),
                    out_img)        

  cl.enqueue_copy(loader.queue, OutImg, out_img).wait()

  # cv2.imwrite("/tmp/sub_cl_notex.jpg", OutImg)
