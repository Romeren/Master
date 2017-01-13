# -*- coding: utf-8 -*-  # NOQA
import json
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous


class Plugin(abstract_plugin):
    def initialize(self, module):
        self.module = module
        self.service_name = "account/login"

    def get(self):
        user = self.get_current_user()
        context = {}
        if user:
            context["username"] = user
        context["location_js"] = self.service_name.replace("/", "\\\/")

        context["address"] = self.get_address()

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

        context["address"] = self.get_address()

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
        
        validator_address = self.get_plugin_addr("account/basic/validate_user")

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

    def get_address(self):
        return self.get_plugin_addr(self.service_name, host=self.module.address)

    def get_plugin_addr(self, service_name, service_type = "rest", service_category="plugin", host="*"):
        info = self.find_plugin(service_type, service_category, service_name, host)
        address = ""
        if info is not None:
            address = "http://" + info["hostname"] + ":" + info["port"] +"/" + info["service_name"]
        return address

config = {"service_name": "account/login",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "plugin"
          }
