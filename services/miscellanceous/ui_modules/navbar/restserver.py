# -*- coding: utf-8 -*-  # NOQA
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Service(abstract_plugin):
    def get(self):
        context = self.get_basic_context()

        context["btns"] = self.__get_nav_btns()

        self.render("html/navbar.html", context=context)

    def __get_nav_btns(self):
        pages = self.find_services(service_type="rest",
                                   service_category="page",
                                   service_name="*")
        btns = []
        for page in pages:
            btns.append(self.get_service_reference_from_request(page))
        return btns

config = {"service_name": "navbar",
          "handler": Service,
          "service_type": "rest",
          "service_category": "ui_module",
          "dependencies": [
              "rest/page"
          ]
          }
