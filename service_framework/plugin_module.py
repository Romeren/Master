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

    def __init__(self, service_configurations):
        self.is_active = True
        self.is_exiting = False
        # self.heartbeat_interval = 120.0
        self.address = "localhost"
        self.port = 5555
        self.pluginPort = None
        self.service_configurations = service_configurations

        # Connect to plugin broker:
        context = zmq.Context()
        print("Connecting to server...")
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://" + self.address + ":" + str(self.port))

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
            paths.append((r'\/' + str(config["service_name"]) + r"\/|\/" + str(config["service_name"]), config["handler"]))  # NOQA

        # set cookie secret:
        cookie_secret = self.application_secret

        # set up tornado frame work:
        self.app = web.Application(paths, cookie_secret=cookie_secret)

        # add listener to port:
        self.app.listen(self.pluginPort)
        print("Module started!")
        ioloop.IOLoop.instance().start()

    def request_config(self):
        self.socket.send(json.dumps({
            "request_config": True,
            "host": self.address
            }))

        #  Get the reply.
        message = self.socket.recv()
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
            self.socket.send(json.dumps(request))
            #  Get the reply.
            message = self.socket.recv()
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
            self.socket.send(json.dumps({
                "service_name": config["service_name"],
                "host_address": self.address,
                "subscribe": False,
                "service_type": config["service_type"],
                "service_category": config["service_category"],
                "port": self.pluginPort}))

            #  Get the reply.
            message = self.socket.recv()
            message = json.loads(message)

            if(message["status"] == 200):
                print("Received reply ", message)
            else:
                print(message)

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
