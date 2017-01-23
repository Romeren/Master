# -*- coding: utf-8 -*-  # NOQA
import json
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous


class Service(abstract_plugin):
    def get(self):
        htmlPath = "html/login.html"
        context = self.get_basic_context()

        ref = "references"
        name = "login"
        context[ref][name] = self.get_service_reference(service_name=name,  # NOQA
                                                            service_type="rest",  # NOQA
                                                            service_category="ui_module")  # NOQA

        self.render(htmlPath, context=context)

    @asynchronous
    @gen.engine
    def post(self):
        print("POST LOGIN")
        htmlPath = "html/login.html"
        context = self.get_basic_context()

        if context["user"]:
            self.render(htmlPath, context)
            return

        ref = "references"
        name = "login"
        context[ref][name] = self.get_service_reference(service_name=name,
                                                        service_type="rest",
                                                        service_category="ui_module")  # NOQA
        context[ref][name]["hasError"] = True
        # get params:
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")

        # Validate username and password:
        pluginname = "account/basic/validate_user"
        validateAddr = self.get_service_address(pluginname)
        if validateAddr is None:
            self.render(htmlPath, context=context)
            return

        params = {'username': username,
                  'password': password}
        future = self.send_external_request(validateAddr,
                                            params,
                                            isPost=True)
        response = yield future

        if response is None or response.body is None:
            context[ref][name]["hasError"] = True
            self.render(htmlPath, context=context)
            return

        response = json.loads(response.body.decode("utf-8"))

        if response["status"] == 200 and response["username"] == username:
            self.set_secure_cookie("user", username)
            context["user"] = username
            context["logedin"] = True
            context[ref][name]["hasError"] = False

        self.render(htmlPath, context=context)


config = {"service_name": "login",
          "handler": Service,
          "service_type": "rest",
          "service_category": "ui_module",
          "dependencies": [
              # topic, topic, topic
              "rest/plugin/account/basic/validate_user"
              ]
          }
