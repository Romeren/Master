# -*- coding: utf-8 -*-  # NOQA
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Service(abstract_plugin):
    def get(self):
        context = self.get_basic_context()

        ref = "references"
        name = "login"
        context[ref][name] = self.get_service_reference(service_name=name,  # NOQA
                                                            service_type="rest",  # NOQA
                                                            service_category="ui_module")  # NOQA

        self.render("html/login.html", context=context)


config = {"service_name": "login",
          "handler": Service,
          "service_type": "rest",
          "service_category": "ui_module",
          "dependencies": [
              # topic, topic, topic
              "rest/ui_modules/login"
              ]
          }
