from worker import Worker

class Drawer(Worker):

  def __init__(self, manager, view):
    '''
    '''
    fovs = view.fovs
    canvases = view.canvases

    #
    # first we need to load and stitch the FoV
    #
    for fov in fovs:
      if not fov._thumbnail:
        fov.load_and_stitch_thumbnails()

      #
      # then, we place the fov pixels on our canvases
      #
      for w in range(len(fov._thumbnail._levels)):
        canvas = canvases[w]

        pixels = fov._thumbnail._levels[w]._pixels

        canvas.place_pixels(pixels, (fov._tx / 4) / 2**w, (fov._ty / 4) / 2**w)




  @staticmethod
  def run(manager, view):
    '''
    '''
    Drawer(manager, view)
