# -*- coding: utf-8 -*-  # NOQA
from service_framework.plugin_module import Plugin_module as framework  # NOQA
from services.pages.login.restserver import config
from services.pages.ui_modules import ui_modules as uim

settings = {
    "ui_modules": {"Rest_Service_Module": uim.Rest_Service_Module,
                   "Websocket_Service_Module": uim.Websock_Service_Module,
                   "Navbar_Module": uim.Navbar_Module,
                   "Footer_Module": uim.Footer_Module,
                   "Head_Module": uim.Head_Module,
                   "About_Module": uim.About_Module
                   },
    }

framework([config], settings=settings)
