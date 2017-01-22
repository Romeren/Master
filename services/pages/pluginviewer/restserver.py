# -*- coding: utf-8 -*-  # NOQA
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Service(abstract_plugin):

    def get(self):
        htmlPath = "html/pluginviewer.html"
        context = self.get_basic_context()
        refs = ["navbar", "footer"]

        slug = self.request.uri
        if slug.startswith("/"):
            slug = slug[1:]

        slug = slug.split("/", 1)

        if len(slug) < 2:
            slug.append("None")

        ref = "references"
        plug = self.get_service_reference(service_name=slug[1],
                                          service_type="rest",
                                          service_category="plugin")
        if plug["address"] is None:
            plug = None
        print("plugin", plug)
        context[ref]["plugin"] = plug
        context = self.set_references(refs, context)
        self.render(htmlPath, context=context)

    def set_references(self, names, context):
        ref = "references"
        for name in names:
            context[ref][name] = self.get_service_reference(service_name=name,  # NOQA
                                                                service_type="rest",  # NOQA
                                                                service_category="ui_module")  # NOQA
        return context


config = {"service_name": "plugin",
          "handler": Service,
          "service_type": "rest",
          "service_category": "page",
          "dependencies": [
              "rest/plugin",
              "socket/plugin",
              "rest/ui_module/navbar",
              "rest/ui_module/footer"
              ]
          }
