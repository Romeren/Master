# -*- coding: utf-8 -*-  # NOQA
import os
from service_framework.plugin_module import Plugin_module as framework  # NOQA
import webserver.ui_modules as uim
from webserver.restserver import config  # NOQA
from tornado.web import StaticFileHandler

server_settings = {
	 "static_path": os.path.join(os.path.dirname(__file__), "static"),
	 "xsrf_cookies": True,
	 "ui_modules": {"Rest_Service_Module": uim.Rest_Service_Module,
                    "Websocket_Service_Module": uim.Websock_Service_Module,
                    "Navbar_Module": uim.Navbar_Module,
                    },
     "port": 8888
}

static_paths = {
	"service_name": "javascripts",
    "handler": StaticFileHandler,
    "service_type": "rest",
    "service_category": "plugin",
    "path": r"/java/(.*)",
    "handler_settings": {'path': "webserver/javascript"}
}

framework([config], settings=server_settings)
