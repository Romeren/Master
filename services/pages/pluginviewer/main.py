# -*- coding: utf-8 -*-  # NOQA

from service_framework.plugin_module import Plugin_module as framework  # NOQA
from services.pages.pluginviewer.restserver import config
from services.pages.ui_modules import ui_modules as uim

settings = {
    "ui_modules": {"Rest_Service_Module": uim.Rest_Service_Module,
                   "Websocket_Service_Module": uim.Websock_Service_Module,
                   "Head_Module": uim.Head_Module,
                   },
    }

framework([config], settings=settings)
