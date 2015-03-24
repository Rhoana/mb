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
      if not fov._imagedata:
        fov.load_and_stitch(view._ratio)

      #
      # then, we place the fov pixels on our canvases
      #
      for w in range(len(fov._imagedata._levels)):
        canvas = canvases[w]

        pixels = fov._imagedata._levels[w]._pixels

        canvas.place_pixels(pixels, (fov._tx / view._ratio) / 2**w, (fov._ty / view._ratio) / 2**w)


      # notify the manager for each FoV
      manager.on_drawing_complete(view)


  @staticmethod
  def run(manager, view):
    '''
    '''
    Drawer(manager, view)
