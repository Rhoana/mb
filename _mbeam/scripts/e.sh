
echo "OpenCV"
time python _mbeam/scripts/cv.py ~/Desktop/021/000001/thumbnail_021_000001_001_2015-01-14T1653216213670.bmp 840 744 5

echo
echo

echo "Byte seeking"
#time python _mbeam/scripts/bmp.py ~/Desktop/021/000001/thumbnail_021_000001_001_2015-01-14T1653216213670.bmp 840 744 5

echo

echo "OpenCL"
time python _mbeam/scripts/cl.py ~/Desktop/021/000001/thumbnail_021_000001_001_2015-01-14T1653216213670.bmp 840 744 5


echo

echo "OpenCL No tex"
time python _mbeam/scripts/cl_notex.py ~/Desktop/021/000001/thumbnail_021_000001_001_2015-01-14T1653216213670.bmp 840 744 5
