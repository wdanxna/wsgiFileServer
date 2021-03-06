import sys
from wsgiref.simple_server import make_server
import boxlib
from boxrouter import boxrouter


PORT = 8051
router = boxrouter(('/upload',          boxlib.upload),
                   ('/download',        boxlib.download),
                   ('/move',            boxlib.move),
                   ('/delete',          boxlib.delete),
                   ('/getpatrolconfig', boxlib.getpatrolconfig),
                   ('/gettrackfile',    boxlib.gettrackfile),
                   ('/getthumbnails',   boxlib.get_thumbnails),
                   ('/rename',          boxlib.rename),
                   ('/filesize',        boxlib.getfilesize),
                   ('/replace',         boxlib.replace),
                   ('/struct',          boxlib.struct),
                   ('/newfolder',       boxlib.createFolder))

httpd = make_server('',PORT,router.start_route)
print 'Starting up HTTP server on port %i...'%PORT
httpd.serve_forever()


def application(env, start_response):
    return router.start_route(env , start_response)