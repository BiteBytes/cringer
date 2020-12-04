#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jinja2
from importlib import import_module
import os

config_file = os.environ.get('CRINGERCONF', 'config.dev')
config = import_module(config_file)

fpath = os.path.realpath(__file__)
TEMPLATES_PATH = os.path.dirname(fpath) + '/templates'
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_PATH))

if __name__ == '__main__':
    from gevent.wsgi import WSGIServer
    from ws.ws import app

    app.debug = True
    port = config.PORT
    print 'Serving in port', port

    http_server = WSGIServer(('', port), app)
    http_server.serve_forever()
