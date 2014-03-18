import sys
from boxdecoder import boxdecoder
ROOT_PATH = "/service"


class boxrouter:
    def __init__(self,*args):
        #reciving (prefix,app) tuples
        self._routes = args

    def start_route(self,environ, start_response):

        path = environ['PATH_INFO']

        for prefix, app in self._routes:
            #if prefix is an empty string or slash, pass path info to the app
            if prefix == '' or prefix == '/':
                return app(environ, start_response)

            if path.startswith(ROOT_PATH+prefix):
                environ['PATH_INFO'] = path[len(ROOT_PATH)+1:]
                decoder = boxdecoder(app)
                return decoder(environ,start_response)

        #do not match anything.
        start_response('404 Not Found',[('Content-Type','text/plain')])
        return ('oops\n',)