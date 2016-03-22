
echo "OpenCV"
time python mbeam/scripts/cv.py ~/Desktop/021/000001/thumbnail_021_000001_001_2015-01-14T1653216213670.bmp 840 744 5

echo
echo

echo "Byte seeking"
#time python mbeam/scripts/bmp.py ~/Desktop/021/000001/thumbnail_021_000001_001_2015-01-14T1653216213670.bmp 840 744 5

echo

echo "OpenCL"
time python mbeam/scripts/cl.py ~/Desktop/021/000001/thumbnail_021_000001_001_2015-01-14T1653216213670.bmp 840 744 5


echo

echo "OpenCL No tex"
time python mbeam/scripts/cl_notex.py ~/Desktop/021/000001/thumbnail_021_000001_001_2015-01-14T1653216213670.bmp 840 744 5
