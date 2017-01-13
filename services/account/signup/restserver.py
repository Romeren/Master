# -*- coding: utf-8 -*-  # NOQA
import json
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous


class Plugin(abstract_plugin):

    def initialize(self, module):
        self.module = module
        self.service_name = "account/signup"

    def get(self):
        context = {}
        context["location_js"] = self.service_name.replace("/", "\\\/")
        
        context["address"] = self.get_address()

        user = self.get_current_user()
        print(user)
        if not user:
            context["hasError"] = False
            self.render("html/signup.html", context=context)
        else:
            self.render("html/signedup.html")

    @asynchronous
    @gen.engine
    def post(self):
        context = {}
        context["location_js"] = self.service_name.replace("/", "\\\/")
        
        context["address"] = self.get_address()

        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        print("SIGNUP_INPUT", username, password)

        if not username or username == "" or username == "None":
            context["hasError"] = True
            self.render("html/signup.html", context=context)
            return

        # check username does not exists
        check_username_addr = self.get_plugin_addr("account/basic/check_username")

        # check username:
        params = {'username': username}
        future = self.send_external_request(check_username_addr,
                                            params,
                                            isPost=True)
        response = yield future
        response = json.loads(response.body)

        # username have been taken:
        if response["status"] == 200:
            context["hasError"] = True
            self.render("html/signup.html", context=context)
            return

        # store username and address
        store_user_addr = self.get_plugin_addr("account/basic/store_user")

        params = {'username': username,
                  'password': password}
        future = self.send_external_request(store_user_addr,
                                            params,
                                            isPost=True)
        response = yield future

        response = json.loads(response.body)

        if response["status"] == 200:
            self.set_secure_cookie("user", username)
            self.render("html/signedup.html")
        else:
            # Error!
            context["hasError"] = True
            self.render("html/signup.html", context=context)
            return

    def get_address(self):
        return self.get_plugin_addr(self.service_name, host=self.module.address)

    def get_plugin_addr(self, service_name, service_type = "rest", service_category="plugin", host="*"):
        info = self.find_plugin(service_type, service_category, service_name, host)
        address = ""
        if info is not None:
            address = "http://" + info["hostname"] + ":" + info["port"] +"/" + info["service_name"]
        return address


config = {"service_name": "account/signup",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "plugin"
          }
