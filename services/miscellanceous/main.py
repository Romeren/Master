# -*- coding: utf-8 -*-  # NOQA
from service_framework.plugin_module import Plugin_module as framework  # NOQA
from services.miscellanceous.javascripts.restserver import config as java  # NOQA
from services.miscellanceous.ui_modules.about.restserver import config as about  # NOQA
from services.miscellanceous.ui_modules.footer.restserver import config as footer  # NOQA
from services.miscellanceous.ui_modules.login.restserver import config as login  # NOQA
from services.miscellanceous.ui_modules.navbar.restserver import config as nav  # NOQA
from services.miscellanceous.ui_modules.signup.restserver import config as signup  # NOQA

framework([java, nav, footer, login, signup, about])
