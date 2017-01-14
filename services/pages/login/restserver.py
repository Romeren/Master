# -*- coding: utf-8 -*-  # NOQA
import json
from services.pages.common.a_handler import Page_handler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous


class Plugin(abstract_plugin):
    def initialize(self, module):
        self.module = module
        self.service_name = "account/login"

    def get(self):
        user = self.get_current_user()
        context = {}
        context = self.set_user_info(user, context)
        context = self.set_basic_context_info(context)

        context = self.set_page_reference(service_name=self.service_name,
                                          context=context,
                                          service_type="rest",
                                          service_category="page")

        self.render("html/login.html", context=context)

    @asynchronous
    @gen.engine
    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        context = {}

        context = self.set_user_info(None, context)
        context = self.set_basic_context_info(context)

        context = self.set_page_reference(service_name=self.service_name,
                                          context=context,
                                          service_type="rest",
                                          service_category="page")

        print(username, password)
        if(not username or
           not password or
           username == "" or
           password == ""):
            context["hasError"] = True
            self.render("html/login.html", context=context)
            return

        # get/check address for validator plugin:
        plugin_address = "account/basic/validate_user"
        validator_address = self.get_plugin_address(plugin_address)

        # check username and password:
        params = {'username': username, 'password': password}
        future = self.send_external_request(validator_address,
                                            params,
                                            isPost=True)
        response = yield(future)

        response = json.loads(response.body)

        if (response["status"] != 200 or
            "username" not in response or
           response["username"] != username):
            context["hasError"] = True
            self.render("html/login.html", context=context)
            return

        self.set_secure_cookie("user", username)
        self.set_user_info(username, context)
        self.render("html/login.html", context=context)
        return

    def get_address(self):
        return self.get_plugin_address(self.service_name,
                                       host=self.module.address)

config = {"service_name": "account/login",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "pages",
          "dependencies": [
              # topic, topic, topic
              "rest/plugin/account/basic/validate_user"
              ]
          }
