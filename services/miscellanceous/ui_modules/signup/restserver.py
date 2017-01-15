# -*- coding: utf-8 -*-  # NOQA
import json
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous


class Service(abstract_plugin):
    def initialize(self, module):
        self.module = module
        self.htmlpath = "html/signup.html"

    def get(self):
        context = self.get_basic_context()

        if context["user"]:
            self.render("html/signup.html", context=context)
            return

        # self pointer:
        ref = "references"
        name = "signup"
        context[ref][name] = self.get_service_reference(service_name=name,  # NOQA
                                                        service_type="rest",  # NOQA
                                                        service_category="page")  # NOQA

        self.render("html/signup.html", context=context)

    @asynchronous
    @gen.engine
    def post(self):
        context = self.get_basic_context()

        # self reference:
        ref = "references"
        name = "signup"
        context[ref][name] = self.get_service_reference(service_name=name,
                                                        context=context,
                                                        service_type="rest",
                                                        service_category="page")  # NOQA

        # if allready loged in....:
        if context["user"]:
            self.render(self.htmlpath, context)
            return

        # get params:
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")

        if not username or username == "" or username == "None":
            context[ref][name]["hasError"] = True
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
            context[ref][name]["hasError"] = True
            self.render(self.htmlpath, context=context)
            return

        response = json.loads(response.body)

        # username have been taken:
        if response["status"] == 200:
            context[ref][name]["hasError"] = True
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
            context[ref][name]["hasError"] = True
            self.render(self.htmlpath, context=context)
            return

        response = json.loads(response.body)

        if response["status"] == 200:
            self.set_secure_cookie("user", username)
            self.render(self.htmlpath, context=context)
        else:
            # Error!
            context[ref][name]["hasError"] = True
            self.render(self.htmlpath, context=context)


config = {"service_name": "signup",
          "handler": Service,
          "service_type": "rest",
          "service_category": "ui_module",
          "dependencies": [
              "rest/page/signup"
          ]
          }
