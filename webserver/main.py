# -*- coding: utf-8 -*-  # NOQA
import os
from service_framework.plugin_module import Plugin_module as framework  # NOQA
from webserver.restserver import config  # NOQA
import webserver.ui_modules as uim

server_settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "xsrf_cookies": True,
    "ui_modules": {"Rest_Service_Module": uim.Rest_Service_Module,
                   "Websocket_Service_Module": uim.Websock_Service_Module,
                   "Navbar_Module": uim.Navbar_Module,
                   },
    "port": 8888
}

framework([config], settings=server_settings)
