import json
import os
import tornado
import tornado.gen
import tornado.web
import tornado.websocket
import urllib


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

    def __init__(self, manager, port=2001, address='127.0.0.1'):
        '''
        '''
        self._manager = manager
        self._port = port
        self._address = address

    def start(self):
        '''
        '''

        address = self._address
        port = self._port

        webapp = tornado.web.Application(
            [
                (r'/tree/(.*)',
                 WebServerHandler,
                 dict(
                     webserver=self)),
                (r'/type/(.*)',
                 WebServerHandler,
                 dict(
                     webserver=self)),
                (r'/content/(.*)',
                 WebServerHandler,
                 dict(
                     webserver=self)),
                (r'/metainfo/(.*)',
                 WebServerHandler,
                 dict(
                     webserver=self)),
                (r'/data/(.*)',
                 WebServerHandler,
                 dict(
                     webserver=self)),
                (r'/debug_mem/(.*)',
                 WebServerHandler,
                 dict(
                     webserver=self)),
                (r'/(.*)',
                 tornado.web.StaticFileHandler,
                 dict(
                     path=os.path.join(
                         os.path.dirname(__file__),
                         'web'),
                     default_filename='index.html'))])

        webapp.listen(
            port,
            address=address,
            max_buffer_size=1024 *
            1024 *
            150000)

        print('Starting webserver at \033[93mhttp://' + address + ':' +
              str(port) + '\033[0m')

        tornado.ioloop.IOLoop.instance().start()


    @tornado.gen.coroutine
    def handle(self, handler):
        '''
        '''
        content = None

        splitted_request = handler.request.uri.split('/')

        path = '/'.join(splitted_request[2:])

        if splitted_request[1] == 'tree':

            data_path = path.split('?')[0]
            parameters = path.split('?')[1].split('&')

            if parameters[0][0] != '_':
                data_path = urllib.unquote(parameters[0].split('=')[1])
            else:
                data_path = None

            content = json.dumps(self._manager.get_tree(data_path))
            content_type = 'text/html'

        elif splitted_request[1] == 'type':

            content = self._manager.check_path_type(path)
            if not content:
                content = 'NULL'
            content_type = 'text/html'

        elif splitted_request[1] == 'content':

            content = json.dumps(self._manager.get_content(path))
            content_type = 'text/html'

        elif splitted_request[1] == 'metainfo':

            content = self._manager.get_meta_info(path)
            content_type = 'text/html'

        elif splitted_request[1] == 'data':

            # this is for actual image data
            path = '/'.join(splitted_request[2:-1])

            tile = splitted_request[-1].split('-')

            x = int(tile[1])
            y = int(tile[2])
            z = int(tile[3])
            w = int(tile[0])

            content = self._manager.get_image(path, x, y, z, w)
            content_type = 'image/jpeg'

        elif splitted_request[1] == 'debug_mem':

            from pympler import asizeof
            content = asizeof.asized(self, detail=7).format().replace('\n','<br/>')
            content += ' '.join(['{}: {}<br/>'.format(ii, kk) for ii, kk in enumerate(self._manager._tiles.keys())])
            content_type = 'text/html'

        # invalid request
        if not content:
            content = 'Error 404'
            content_type = 'text/html'

        # handler.set_header('Cache-Control',
        #                    'no-cache, no-store, must-revalidate')
        # handler.set_header('Pragma','no-cache')
        # handler.set_header('Expires','0')
        handler.set_header('Access-Control-Allow-Origin', '*')
        handler.set_header('Content-Type', content_type)
        handler.write(content)
