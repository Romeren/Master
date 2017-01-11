# -*- coding: utf-8 -*-  # NOQA

from service_framework.plugin_module import Plugin_module as framework  # NOQA
from services.account.basic_functionality.check_username.restserver import config as check  # NOQA
from services.account.basic_functionality.store_user.restserver import config as store  # NOQA
from services.account.basic_functionality.validate_user.restserver import config as validate  # NOQA
from services.account.login.restserver import config as login
from services.account.signup.restserver import config as signup

framework([login,
           validate,
           store,
           check,
           signup])
