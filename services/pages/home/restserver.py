# -*- coding: utf-8 -*-  # NOQA
from services.pages.common.a_handler import Page_handler as abstract_plugin  # NOQA


class Plugin(abstract_plugin):
    def initialize(self, module):
        self.module = module
        self.service_name = "home"

    def get(self):
        html_path = "html/home.html"
        context = {}
        user = self.get_secure_cookie("user")
        context = self.set_user_info(user, context)
        context = self.set_basic_context_info(context)

        context = self.set_page_reference(service_name="account/signup",
                                          context=context,
                                          service_type="rest",
                                          service_category="page")

        self.render(html_path, context=context)

    def get_plugin_formed(self,
                          service_name,
                          service_category,
                          service_type="*"):
        message = self.find_plugin(service_type,
                                   service_category,
                                   service_name)
        print("get_plugin", message)
        if message is None:
            return {"content": "No module found", "type": "text"}
        else:
            return {"type": message["service_type"],
                    "content": message}

config = {"service_name": "home",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "page",
          "dependencies": [
              "rest/plugin/account/signup",
              "rest/page/about",
              "rest/miscellanceous/javascripts"
          ]
          }
