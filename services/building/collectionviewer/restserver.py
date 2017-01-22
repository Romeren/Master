# -*- coding: utf-8 -*-  # NOQA
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
        # ref = "references"
        # name = "building/collectionviewer"
        # context[ref][name] = self.get_service_reference(service_name=name,
        #                                                service_type="rest",
        #                                                service_category="ui_module")  # NOQA
        pluginname = "building/entity"
        addr = self.get_service_address(pluginname)
        if addr is None:
            self.render(htmlPath, context=context)
            return

        # print(addr)
        params = {'username': context["user"]}
        future = self.send_external_request(addr,
                                            params,
                                            isPost=False)
        response = yield future

        print(response)
        self.render(htmlPath, context=context)

    def post(self):
        pass


config = {"service_name": "building/collectionviewer",
          "handler": Service,
          "service_type": "rest",
          "service_category": "plugin",
          "dependencies": [
              # topic, topic, topic
              "rest/plugin/building/entity"
              ]
          }
