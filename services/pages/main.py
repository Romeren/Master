# -*- coding: utf-8 -*-  # NOQA
from service_framework.plugin_module import Plugin_module as framework  # NOQA
from services.pages.home.restserver import config as home  # NOQA
from services.pages.login.restserver import config as login  # NOQA
from services.pages.signup.restserver import config as signup  # NOQA
from services.pages.ui_modules import ui_modules as uim

server_settings = {
    "ui_modules": {"Rest_Service_Module": uim.Rest_Service_Module,
                   "Websocket_Service_Module": uim.Websock_Service_Module,
                   "Head_Module": uim.Head_Module
                   },
}

framework([home, login, signup], settings=server_settings)
