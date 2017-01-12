# -*- coding: utf-8 -*-  # NOQA

from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Plugin(abstract_plugin):
    def initialize(self, module):
        self.module = module
        # urls and command attachment:
        self.paths = []
        self.pathCmd = {}
        self.paths.append("plugin")
        self.pathCmd["plugin"] = self.get_plugin
        self.paths.append("")
        self.pathCmd[""] = self.get_home_page

    def get(self):
        slug = self.request.uri
        if slug.startswith("/"):
            slug = slug[1:]
        elif slug is None or slug == "":
            self.write("404: BAD URL!")

        slug = slug.split("/", 1)

        if slug[0] in self.paths:
            context = {}
            user = self.get_secure_cookie("user")
            context = self.set_user_info(user, context)

            method = self.pathCmd[slug[0]]
            if len(slug) > 1:
                method(context, slug[1])
            else:
                method(context, None)
        # else:
        #    self.write("404: BAD URL!")

    def get_plugin(self, context, slug):
        message = "Error! "
        html_path = "html/browse_plugin.html"
        context = context

        # Check input parameters:
        if slug is None or slug == "":
            message += "-No parameters"
            context["plugin"] = {"content": message,
                                 "type": "text"}
            self.render(html_path, context=context)
            return

        # request plugin at broker:
        context["plugin"] = self.get_plugin_formed(slug, "plugin")  # NOQA

        self.render(html_path, context=context)

    def get_home_page(self, context, slug):
        html_path = "html/home_page.html"
        context = context

        # request about plugin at broker:
        context["about"] = self.get_plugin_formed("miscellaneous/about", "plugin")  # NOQA
        if context["loggedin"]:
            self.render(html_path, context=context)
            return
        # request signup plugin at broker:
        context["signup"] = self.get_plugin_formed("account/signup", "plugin")  # NOQA

        self.render(html_path, context=context)

    def set_user_info(self, user, context):
        if user:
            context["loggedin"] = True
            context["user"] = user
        else:
            context["loggedin"] = False
            context["user"] = None
        return context

    def get_plugin_formed(self, service_name, service_category):
        message = self.find_plugin(service_name, service_category)
        if message is None:
            return {"content": "No module found", "type": "text"}
        else:
            return {"type": message["service_type"],
                    "content": message}

config = {"service_name": "home",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "plugin",
          "path": r"^(?!\/java).*$",
          }




# thread = Thread(target=broker_event_subscriber,
#                args=("localhost", 5556))
# thread.start()
