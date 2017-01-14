# -*- coding: utf-8 -*-  # NOQA
from tornado.web import UIModule


class Rest_Service_Module(UIModule):
    def render(self, service_info):
        service_info["service_name_js"] = service_info["service_name"].replace("/", "\\\/")  # NOQA
        return self.render_string(
            "html/rest_template.html", content=service_info)


class Websock_Service_Module(UIModule):

    def render(self, service_info):
        service_info["service_name_js"] = service_info["service_name"].replace("/", "\\\/")  # NOQA
        return self.render_string(
            "html/websocket_template.html", content=service_info)


class Head_Module(UIModule):
    def render(self, context):
        return self.render_string(
            "html/head.html", context=context)


class Navbar_Module(UIModule):
    def render(self, context):
        return self.render_string(
            "html/navbar.html", context=context)


class About_Module(UIModule):
    def render(self, context):
        return self.render_string(
            "html/about.html", context=context)


class Footer_Module(UIModule):
    def render(self, context):
        return self.render_string(
            "html/footer.html", context=context)


class Login_Module(UIModule):
    def render(self, context):
        return self.render_string(
            "html/login.html", context=context)


class Signup_Module(UIModule):
    def render(self, context):
        return self.render_string(
            "html/signup.html", context=context)
