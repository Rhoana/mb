import os
import socket
import time
import tornado
import tornado.gen
import tornado.web
import tornado.websocket

cl = []

class WebSocketHandler(tornado.websocket.WebSocketHandler):

  def initialize(self, manager):
    '''
    '''
    self._manager = manager
    self._controller = self._manager._websocket_controller

  def open(self):
    '''
    '''
    if self not in cl:
      cl.append(self)

    self._controller.handshake(self)

  def check_origin(self, origin):
    '''
    '''
    return True

  def on_close(self):
    '''
    '''
    if self in cl:
      cl.remove(self)

  def on_message(self, message):
    '''
    '''
    self._controller.on_message(message)

  def send(self, message, binary=False):
    '''
    Sends a message to a single client.
    '''
    self.write_message(message, binary=binary)

  def broadcast(self, message, binary=False):
    '''
    Sends a message to all connected clients.
    '''
    for c in cl:
      c.write_message(message, binary=binary)


class WebServerHandler(tornado.web.RequestHandler):

  def initialize(self, webserver):
    self._webserver = webserver

  @tornado.web.asynchronous
  @tornado.gen.coroutine
  def get(self, uri):
    '''
    '''
    self._webserver.handle(self)


class WebServer:

  def __init__( self, manager, port=2001 ):
    '''
    '''
    self._manager = manager
    self._port = port

  def start( self ):
    '''
    '''

    ip = socket.gethostbyname('')
    port = self._port

    webapp = tornado.web.Application([

      (r'/ws', WebSocketHandler, dict(manager=self._manager)),
      
      (r'/data/(.*)', WebServerHandler, dict(webserver=self)),
      (r'/(.*)', tornado.web.StaticFileHandler, dict(path=os.path.join(os.path.dirname(__file__),'../web'), default_filename='index.html'))
  
    ])

    webapp.listen(port, max_buffer_size=1024*1024*150000)

    print 'Starting webserver at \033[93mhttp://' + ip + ':' + str(port) + '\033[0m'

    tornado.ioloop.PeriodicCallback(self._manager.tick, 200).start()
    tornado.ioloop.IOLoop.instance().start()

  @tornado.gen.coroutine
  def handle( self, handler ):
    '''
    '''
    content = None

    splitted_request = handler.request.uri.split('/')
    path = '/'.join(splitted_request[2:-1])
    tile = splitted_request[-1].split('-')

    x = int(tile[1])
    y = int(tile[2])
    z = int(tile[3])
    w = int(tile[0])

    content = self._manager.get_image(path, x, y, z, w)
    content_type = 'image/jpeg'
    # TODO

    

    # invalid request
    if not content:
      content = 'Error 404'
      content_type = 'text/html'

    handler.set_header('Cache-Control','no-cache, no-store, must-revalidate')
    handler.set_header('Pragma','no-cache')
    handler.set_header('Expires','0')
    handler.set_header('Access-Control-Allow-Origin', '*')
    handler.set_header('Content-Type', content_type)
    handler.write(content)
