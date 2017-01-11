# -*- coding: utf-8 -*-  # NOQA
import json
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous

validator_address = None
host_address = None


class Plugin(abstract_plugin):
    def initialize(self):
        self.service_name = "account/login"

        global host_address
        if host_address is None:
            host_address = self.get_external_plugin_address(self.service_name,
                                                            "rest")

    def get(self):
        user = self.get_current_user()
        context = {}
        if user:
            context["username"] = user
        context["location_js"] = self.service_name.replace("/", "\\\/")
        global host_address
        context["address"] = host_address

        if not user:
            context["hasError"] = False
            self.render("html/login.html", context=context)
        else:
            context["username"] = user
            self.render("html/loggedin.html", context=context)

    @asynchronous
    @gen.engine
    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        context = {}
        context["location_js"] = self.service_name.replace("/", "\\\/")
        global host_address
        context["address"] = host_address

        print(username, password)
        if(not username or
           not password or
           username == "" or
           password == ""):
            context["hasError"] = True
            self.render("html/login.html", context=context)
            return

        context["username"] = username
        # get/check address for validator plugin:
        global validator_address
        if validator_address is None:
            validator_address = self.get_external_plugin_address("*/validate_user", "rest")  # NOQA
            print(validator_address)

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
        self.render("html/loggedin.html", context=context)
        return

config = {"service_name": "account/login",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "plugin"
          }
