import os
import sys
import urllib
from cStringIO import StringIO
'''
This is a character decoder middleware
'''
class boxdecoder(object):
    def __init__(self,app):
        self.wrapped_app = app
        return

    def __call__(self, environ, start_response):

        def decode(environ):
            #decode path then put back decoded path
            length = int(environ.get('CONTENT_LENGTH','0'))
            meta = environ['wsgi.input'].read(length)
            #try to decode percentage
            meta = urllib.unquote(meta)
            environ['wsgi.input'] = StringIO(meta)
            environ['CONTENT_LENGTH'] = str(len(meta))
            return environ

        def start_response_wrapper(status,response_headers, exc_info=None):
            #we don't need to do any thing for now.
            #we ignore the return value from start_response
            start_response(status,response_headers,exc_info)
            def dummy_write(data):
                raise RuntimeError('decoder does not support the deprecated write() callable in wsgi clients')

            return dummy_write

        iterable = self.wrapped_app(decode(environ),start_response_wrapper)
        #we don't need to encode back
        return iterable

