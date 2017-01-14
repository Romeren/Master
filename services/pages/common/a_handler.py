# -*- coding: utf-8 -*-  # NOQA
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Page_handler(abstract_plugin):

    def set_page_reference(self,
                           service_name,
                           context,
                           service_category="page",
                           service_type="rest"):
        context["locations"][service_name] = {
            "location_js": service_name.replace("/", "\\\/"),
            "address": self.get_plugin_address(service_name=service_name,
                                               service_type=service_type,
                                               service_category=service_category),  # NOQA
            "hasError": False
        }
        return context

    def set_basic_context_info(self, context):
        fields = ["javascripts", "miscellanceous"]
        context[fields[0]] = self.get_plugin_address(fields[0],
                                                     service_category=fields[1]
                                                     )
        context["navbar_btn"] = self.__getnav_btns()
        context["locations"] = {}
        return context

    def set_user_info(self, user, context):
        if user:
            context["loggedin"] = True
            context["user"] = user
        else:
            context["loggedin"] = False
            context["user"] = None
        return context

    def __getnav_btns(self):
        pages = self.find_plugins(service_type="rest",
                                  service_category="page",
                                  service_name="*")
        btns = []
        for page in pages:
            btns.append(self.__page_to_btn(page))

        return btns

    def __page_to_btn(self, page):
        pass
