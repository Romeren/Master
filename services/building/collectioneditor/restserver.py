# -*- coding: utf-8 -*-  # NOQA
import json
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous


class Service(abstract_plugin):

    @asynchronous
    @gen.engine
    def get(self):
        htmlPath = "html/collectioneditor.html"
        context = self.get_basic_context()

        self.render(htmlPath, context=context)


    def __get_addr_handle_error(self, pluginname, error_msg, context, htmlPath):
        addr = self.get_service_address(pluginname)
        if addr is None:
          self.__send_error_response(context, error_msg, htmlPath)
        return addr

    def __send_error_response(self, context, error_msg, htmlPath):
        context["message"] = error_msg
        self.render(htmlPath, context=context)

config = {"service_name": "building/collectioneditor",
          "handler": Service,
          "service_type": "rest",
          "service_category": "plugin",
          "dependencies": [
              ]
          }
