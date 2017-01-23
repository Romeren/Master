# -*- coding: utf-8 -*-  # NOQA
import json
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous


class Service(abstract_plugin):

    @asynchronous
    @gen.engine
    def get(self):
        htmlPath = "html/collectionviewer.html"
        context = self.get_basic_context()

        if context["user"] is None:
            self.render(htmlPath, context=context)
            return
       
        # add dependency to self:
        ref = "references"
        name = "building/collectionviewer"
        context[ref][name] = self.get_service_reference(service_name=name,
                                                        service_type="rest",
                                                        service_category="plugin")  # NOQA

        # add dependency to building editor:
        ref = "references"
        name = "building/collectioneditor"
        context[ref][name] = self.get_service_reference(service_name=name,
                                                        service_type="rest",
                                                        service_category="plugin")  # NOQA

         # print(addr)
        addr = self.__get_addr_handle_error("account/ownership",
                                            "The service providing functionality for account ownership is down, please try again later",
                                            context,
                                            htmlPath)
        if not addr:
          return

        params = {'username': context["user"],
                  'service': "building/entity"}
        future = self.send_external_request(addr,
                                            params,
                                            isPost=False)

        response = yield future

        if response is None or response.body is None:
          self.__send_error_response(context, "Faild to get users permisions, try again...", htmlPath)
          return

        try:
          print(response.body)
          response = json.loads(response.body.decode("utf-8"))
        except:
          self.__send_error_response(context, "Faild to get users permisions, try again...", htmlPath)
          return

        if(response["status"] != 200):
          self.__send_error_response(context, response, htmlPath)
          return

        permissions = response["permissions"]

        if len(permissions) < 1:
          self.__send_error_response(context, "There are no entities asociated with the user.... please create one or more!", htmlPath)
          return

        addr = self.__get_addr_handle_error("building/entity",
                                            "The service providing functionality for building entities is down, please try again later",
                                            context,
                                            htmlPath)

        if not addr:
          return

        entities = []
        for p in permissions:
          print("permision", p)
          params = {'entity': p["indentifier"]}
          future = self.send_external_request(addr,
                                            params,
                                            isPost=False)
          response = yield future

          if response is None or response.body is None:
              continue
          response = json.loads(response.body)
          
          if response["status"] != 200:
            continue

          entities.append(response["entity"])

        context["entities"] = entities
        context["message"] = json.dumps(entities) # TODO(REMOVE): remove this statement, its for debuging!
        self.render(htmlPath, context=context)


    def __get_addr_handle_error(self, pluginname, error_msg, context, htmlPath):
        addr = self.get_service_address(pluginname)
        if addr is None:
          self.__send_error_response(context, error_msg, htmlPath)
        return addr

    def __send_error_response(self, context, error_msg, htmlPath):
        context["message"] = error_msg
        self.render(htmlPath, context=context)

config = {"service_name": "building/collectionviewer",
          "handler": Service,
          "service_type": "rest",
          "service_category": "plugin",
          "dependencies": [
              # topic, topic, topic
              "rest/plugin/building/collectioneditor",
              "rest/plugin/account/ownership",
              "rest/plugin/building/entity"
              ]
          }
