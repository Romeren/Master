# -*- coding: utf-8 -*-  # NOQA
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Service(abstract_plugin):
    def initialize(self, module):
        self.module = module
        self.service_name = "account/login"

    def get(self):
        context = self.get_basic_context()

        refs = ["footer", "about", "navbar", "login"]

        context = self.set_references(refs, context)

        self.render("html/login.html", context=context)

    def set_references(self, names, context):
        ref = "references"
        for name in names:
            context[ref][name] = self.get_service_reference(service_name=name,  # NOQA
                                                                service_type="rest",  # NOQA
                                                                service_category="ui_module")  # NOQA
        return context


config = {"service_name": "account/login",
          "handler": Service,
          "service_type": "rest",
          "service_category": "page",
          "dependencies": [
              # topic, topic, topic
              "rest/plugin/account/basic/validate_user"
              ]
          }
