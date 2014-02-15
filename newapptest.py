import sys
from wsgiref.simple_server import make_server
import boxlib
from boxrouter import boxrouter


PORT = 8051
router = boxrouter(('/upload',boxlib.upload),
                   ('/download',boxlib.download),
                   ('/move',boxlib.move),
                   ('/fetchconfig',boxlib.fetchconfig),
                   ('/gettrackfile',boxlib.gettrackfile),
                   ('/getthumbnails',boxlib.get_thumbnails))

httpd = make_server('',PORT,router)
print 'Starting up HTTP server on port %i...'%PORT

httpd.serve_forever()