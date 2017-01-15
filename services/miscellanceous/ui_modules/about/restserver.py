# -*- coding: utf-8 -*-  # NOQA
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Service(abstract_plugin):
    def get(self):
        context = self.get_basic_context()

        self.render("html/about.html", context=context)

config = {"service_name": "about",
          "handler": Service,
          "service_type": "rest",
          "service_category": "ui_module",
          }
