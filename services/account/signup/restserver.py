# -*- coding: utf-8 -*-  # NOQA
import json
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous

check_username_addr = None
store_user_addr = None
host_address = None


class Plugin(abstract_plugin):
    def initialize(self):
        self.service_name = "account/signup"

        global host_address
        if host_address is None:
            host_address = self.get_external_plugin_address(self.service_name,
                                                            "rest")

    def get(self):
        context = {}
        context["location_js"] = self.service_name.replace("/", "\\\/")
        global host_address
        context["address"] = host_address

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
        global host_address
        context["address"] = host_address
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        print("SIGNUP_INPUT", username, password)

        if not username or username == "" or username == "None":
            context["hasError"] = True
            self.render("html/signup.html", context=context)
            return

        # check username does not exists
        global check_username_addr
        if check_username_addr is None:
            check_username_addr = self.get_external_plugin_address("*/check_username",  # NOQA
                                                                   "rest")
            print("CHECKUSERADDR", check_username_addr)

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
        global store_user_addr
        if store_user_addr is None:
            store_user_addr = self.get_external_plugin_address("*/store_user",
                                                               "rest")
            print("STOREADDR", store_user_addr)

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

config = {"service_name": "account/signup",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "plugin"
          }
