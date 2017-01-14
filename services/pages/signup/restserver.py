# -*- coding: utf-8 -*-  # NOQA
import json
from services.pages.common.a_handler import Page_handler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous


class Plugin(abstract_plugin):

    def initialize(self, module):
        self.module = module
        self.service_name = "account/signup"
        self.htmlpath = "html/signup.html"

    def get(self):
        user = self.get_current_user()
        context = {}

        context = self.set_basic_context_info(context)
        context = self.set_user_info(user, context)

        context = self.set_page_reference(service_name=self.service_name,
                                          context=context,
                                          service_type="rest",
                                          service_category="page")

        self.render(self.htmlpath, context=context)

    @asynchronous
    @gen.engine
    def post(self):
        user = self.get_current_user()
        context = {}

        context = self.set_basic_context_info(context)
        context = self.set_user_info(user, context)

        context = self.set_page_reference(service_name=self.service_name,
                                          context=context,
                                          service_type="rest",
                                          service_category="page")

        # if allready loged in....:
        if user:
            self.render(self.htmlpath, context)
            return

        # get params:
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")

        if not username or username == "" or username == "None":
            context["locations"][self.service_name]["hasError"] = True
            self.render(self.htmlpath, context=context)
            return

        # check username does not exists
        pluginname = "account/basic/check_username"
        check_username_addr = self.get_plugin_address(pluginname)

        # check username:
        params = {'username': username}
        future = self.send_external_request(check_username_addr,
                                            params,
                                            isPost=True)
        response = yield future
        if response is None:
            context["locations"][self.service_name]["hasError"] = True
            self.render(self.htmlpath, context=context)
            return

        response = json.loads(response.body)

        # username have been taken:
        if response["status"] == 200:
            context["locations"][self.service_name]["hasError"] = True
            self.render(self.htmlpath, context)
            return

        # store username and address
        pluginname = "account/basic/store_user"
        store_user_addr = self.get_plugin_address(pluginname)

        params = {'username': username,
                  'password': password}
        future = self.send_external_request(store_user_addr,
                                            params,
                                            isPost=True)
        response = yield future

        if response is None:
            context["locations"][self.service_name]["hasError"] = True
            self.render(self.htmlpath, context=context)
            return

        response = json.loads(response.body)

        if response["status"] == 200:
            self.set_secure_cookie("user", username)
            self.render(self.htmlpath, context=context)
        else:
            # Error!
            context["locations"][self.service_name]["hasError"] = True
            self.render(self.htmlpath, context=context)

    def get_address(self):
        return self.get_plugin_address(self.service_name,
                                       host=self.module.address)

config = {"service_name": "account/signup",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "page",
          "dependencies": [
              # topic, topic, topic
              "rest/plugin/account/basic/store_user",
              "rest/plugin/account/basic/check_username"
              ]
          }
