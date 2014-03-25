import os
import sys
import re
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
            if environ["PATH_INFO"]=="upload":
                #print meta
                #handle filename instead all meta data
                file_name_list = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', meta)
                if len(file_name_list) > 0:
                    origin_file_name = file_name_list[0]
                    fix_file_name = urllib.unquote(origin_file_name)
                    meta = meta.replace(origin_file_name,fix_file_name)
            else:
                meta = urllib.unquote(meta)
                #print 'normal meta fix: '+meta

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

