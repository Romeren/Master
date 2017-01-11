# -*- coding: utf-8 -*-  # NOQA
import fnmatch
import json
import os
import re
import tornado.ioloop
import tornado.web
import zmq
from threading import Thread
plugins = {}


class MainHandler(tornado.web.RequestHandler):

    def initialize(self):
        # Component broker:
        self.broker_address = "localhost"
        self.broker_port = 5555
        self.service_types = ["rest", "websocket"]

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

    def find_plugin(self, service_name, service_category):
        # request plugin at broker:
        topic = self.__build_topic("*", service_category, service_name, "*")
        clients = self.__get_matching(plugins, topic)
        try:
            service = clients.next()
        except Exception:
            return None
        return service
        """
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        bk_url = "tcp://" + self.broker_address + ":" + str(self.broker_port)
        socket.connect(bk_url)

        self.socket_send(socket, {"get_service": {
            "service_name": service_name,
            "service_category": service_category
            }
            })

        message = socket.recv()
        message = json.loads(message)
        socket.close()
        return message
        """
    def __build_topic(self,
                      service_type,
                      service_category,
                      service_name,
                      host_address):
        topic = service_type + "/" + service_category + "/" + service_name + "/" + host_address  # NOQA
        return topic

    def __get_matching(self, dictionary, topic):
        regex = fnmatch.translate(str(topic))
        reObj = re.compile(regex)
        return (key for key in dictionary if reObj.search(key))

    def socket_send(self, socket, json_obj):
        socket.send(json.dumps(json_obj))


class Rest_Service_Module(tornado.web.UIModule):
    def render(self, service_info):
        service_info["service_name_js"] = service_info["service_name"].replace("/", "\\\/")  # NOQA
        return self.render_string(
            "html/rest_template.html", content=service_info)


class Websock_Service_Module(tornado.web.UIModule):

    def render(self, service_info):
        service_info["service_name_js"] = service_info["service_name"].replace("/", "\\\/")  # NOQA
        return self.render_string(
            "html/websocket_template.html", content=service_info)


class Navbar_Module(tornado.web.UIModule):
    def render(self, user):
        return self.render_string(
            "html/navbar.html", user=user)


class Server(object):

    def __init__(self):
        self.port = 8888
        self.settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            "login_url": "/login",
            "xsrf_cookies": True,
            "ui_modules": {"Rest_Service_Module": Rest_Service_Module,
                           "Websocket_Service_Module": Websock_Service_Module,
                           "Navbar_Module": Navbar_Module,
                           }
        }

        self.webserverThread = None
        self.app = None

    def make_app(self):
        javascr = "webserver/javascript"
        self.app = tornado.web.Application([
            # (r"/", MainHandler),
            (r"/java/(.*)", tornado.web.StaticFileHandler, {'path': javascr}),
            ], **self.settings)
        self.app.listen(self.port)

    def start(self):
        handlers = [(r"^(?!\/java).*$", MainHandler), ]
        self.app.add_handlers(".*$", handlers)
        tornado.ioloop.IOLoop.current().start()

    def stop(self):
        self.webserverThread.stop()


isRunning = True


def broker_event_subscriber(broker_address, broker_port):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    bk_url = "tcp://" + broker_address + ":" + str(broker_port)
    socket.connect(bk_url)

    topics = ["service/removed", "service/added"]
    for topic in topics:
        socket.setsockopt(zmq.SUBSCRIBE, topic)

    while isRunning:
        content = socket.recv().split(" ", 1)
        info = json.loads(content[1])
        if content[0] == topics[0]:
            topic = __build_topic_from_request(info)
            print("REMOVED:", topic)
            plugins.pop(topic, None)
        else:
            topic = __build_topic_from_request(info)
            print("ADDED:", topic)
            plugins[topic] = info


def __build_topic_from_request(request):
    service_type = "*"
    service_category = "*"
    service_name = "*"
    host_address = "*"
    if("service_type" in request):
        service_type = request["service_type"]
    if("service_name" in request):
        service_name = request["service_name"]
    if("host_address" in request):
        host_address = request["host_address"]
    if("service_category" in request):
        service_category = request["service_category"]

    return __build_topic(service_type,
                         service_category,
                         service_name,
                         host_address)


def __build_topic(service_type,
                  service_category,
                  service_name,
                  host_address):
    topic = service_type + "/" + service_category + "/" + service_name + "/" + host_address  # NOQA
    return topic


thread = Thread(target=broker_event_subscriber,
                args=("localhost", 5556))
thread.start()

if __name__ == "__main__":
    server = Server()
    server.make_app()
    server.start()
isRunning = False
thread.exit()
