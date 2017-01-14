# -*- coding: utf-8 -*-  # NOQA
from tornado.web import StaticFileHandler

config = {
    "service_name": "javascripts",
    "handler": StaticFileHandler,
    "service_type": "rest",
    "service_category": "miscellanceous",
    "path": r"/javascripts/(.*)",
    "handler_settings": {'path': "services/miscellanceous/javascripts/scripts"}
}
