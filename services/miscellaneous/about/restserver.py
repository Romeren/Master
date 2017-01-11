# -*- coding: utf-8 -*-  # NOQA
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Plugin(abstract_plugin):
    def initialize(self):
        self.service_name = "miscellaneous/about"

    def get(self):
        html_path = "html/about.html"
        self.render(html_path)

config = {"service_name": "miscellaneous/about",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "plugin"
          }
