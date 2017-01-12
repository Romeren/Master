# -*- coding: utf-8 -*-  # NOQA
""" Wrapper for implementations of plugins!
handles subscriping to server and sending heartbeats.
"""

import atexit
import json
import signal
from tornado import web, ioloop  # NOQA
import zmq


class Plugin_module(object):

    def __init__(self, service_configurations, settings={}):
        self.is_active = True
        self.is_exiting = False
        # self.heartbeat_interval = 120.0
        self.address = "localhost"
        self.port = 5555
        self.pluginPort = None
        self.service_configurations = service_configurations
        self.settings = settings

        app = self.configure_module()
        
        

        self.start_webserver(app)

# --------------------------------------------------------
# Broker request functions
# --------------------------------------------------------
    def start_webserver(self, app):
        # add listener to port:
        app.listen(self.pluginPort)
        print("Module started!")
        ioloop.IOLoop.instance().start()

    def configure_module(self):
        # Connect to plugin broker:
        self.__connect_to_broker()

        # Request configuration:
        #   - Request available port
        self.request_config()

        # Subscribe module to plugin broker:
        self.subscribe_to_broker()

        # Add exit handler:
        atexit.register(self.termination_handler)
        # add interrupt handler
        signal.signal(signal.SIGINT, self.exit_handler)

        # configure tornado server for handling websockets:
        if(self.pluginPort is None):
            print("plugin port not configured!")
            exit()

        # build paths:
        paths = []
        for config in self.service_configurations:
            paths.append(self.__make_path_config(config))

        # set cookie secret:
        self.settings["cookie_secret"] = self.application_secret

        # set up tornado frame work:
        return web.Application(paths, **self.settings)

    def __connect_to_broker(self):
        # Connect to plugin broker:
        context = zmq.Context()
        print("Connecting to server...")
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://" + self.address + ":" + str(self.port))

    def request_config(self):
        request = {
                "request_config": True,
                "host": self.address
            }
        if "port" in self.settings:
            request["port"] = self.settings["port"]
            del self.settings["port"]
        
        self.socket.send_string(json.dumps(request))

        #  Get the reply.
        message = self.socket.recv_string()
        message = json.loads(message)
        if(message["status"] == 200):
            print("Received reply ", message)
            self.pluginPort = message["port"]
            self.application_secret = message["application_secret"]
        else:
            print(message)
            self.is_active = False
            exit()

    def subscribe_to_broker(self):
        for config in self.service_configurations:
            request = {
                "service_name": config["service_name"],
                "host_address": self.address,
                "subscribe": True,
                "service_type": config["service_type"],
                "service_category": config["service_category"],
                "port": self.pluginPort}
            self.socket.send_string(json.dumps(request))
            #  Get the reply.
            message = self.socket.recv_string()
            message = json.loads(message)
            if(message["status"] == 200):
                print("Received reply ", message)
                self.pluginPort = message["port"]
            else:
                print(message)
                self.is_active = False
                exit()

    def unsubscriped_from_broker(self):
        self.is_active = False
        for config in self.service_configurations:
            self.socket.send_string(json.dumps({
                "service_name": config["service_name"],
                "host_address": self.address,
                "subscribe": False,
                "service_type": config["service_type"],
                "service_category": config["service_category"],
                "port": self.pluginPort}))

            #  Get the reply.
            message = self.socket.recv_string()
            message = json.loads(message)

            if(message["status"] == 200):
                print("Received reply ", message)
            else:
                print(message)

# --------------------------------------------------------
# Publish subscripe functions 
# --------------------------------------------------------
    def broker_event_subscriber(self, broker_address, broker_port):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        bk_url = "tcp://" + broker_address + ":" + str(broker_port)
        socket.connect(bk_url)

        topics = ["service/removed", "service/added"]
        for topic in topics:
            socket.setsockopt_string(zmq.SUBSCRIBE, topic)

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


# --------------------------------------------------------
# Utiliy functions
# --------------------------------------------------------
    def __make_path_config(self, config):
        if "path" in config and "handler_settings" in config:
            config["handler_settings"]["module"] = self
            return (config["path"], config["handler"], config["handler_settings"])
        elif "path" in config:
            return (config["path"], config["handler"], {"module": self})
        elif "handler_settings" in config:
            config["handler_settings"]["module"] = self
            return (self.__make_fall_back_path(config["service_name"]), config["handler"], config["handler_settings"])
        else:
            return (self.__make_fall_back_path(config["service_name"]), config["handler"], {"module": self})

    def __make_fall_back_path(self, service_name):
        return r'\/' + str(service_name) + r"\/|\/" + str(service_name)

    def __build_topic_from_request(self, request):
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

    def __build_topic(self,
                  service_type,
                  service_category,
                  service_name,
                  host_address):
        topic = service_type + "/" + service_category + "/" + service_name + "/" + host_address  # NOQA
        return topic


# --------------------------------------------------------
# Exit and termination handlers:
# --------------------------------------------------------
    def termination_handler(self):
        print("Terminating...")
        self.unsubscriped_from_broker()
        if(self.is_exiting):
            ioloop.IOLoop.instance().stop()
            self.is_exiting = False

    def exit_handler(self, signal, frame):
        print("INTERRUPTED! -terminating")
        if(self.is_exiting):
            ioloop.IOLoop.instance().stop()
            self.is_exiting = False
        exit()
