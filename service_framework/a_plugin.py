# -*- coding: utf-8 -*-  # NOQA
""" sample implementation of a plugin
"""
# from plugin_module import Plugin_module
import json
from tornado import gen
from tornado import httpclient
from tornado import web
from tornado import websocket
import urllib
cl = []


class SocketHandler(websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super(websocket.WebSocketHandler, self).__init__(application,
                                                         request,
                                                         **kwargs)

    def register_event(self, on_message, function):
        if(hasattr(self, "messages_for_listening") is False):
            self.messages_for_listening = {}
        if(on_message in self.messages_for_listening):
            print("Message allready in events! and will be replaced!")
            self.messages_for_listening[on_message] = function
        else:
            self.messages_for_listening[on_message] = function

    def check_origin(self, origin):
        return True

    def open(self):
        print("Connection opened!")
        if self not in cl:
            cl.append(self)

            # TODO(SECURITY): handle authentication and premissions
            self.user = self.get_current_user()
        if("on_open" in self.messages_for_listening):
            message = {"event": "on_open", "message": "connection opened"}
            self.messages_for_listening["on_open"](message)

    def on_message(self, message):
        jsonMsg = None
        try:
            print(message)
            jsonMsg = json.loads(message)
        except Exception:
            print("MESSAGE COULD NOT BE PARSED!")
            self.write_message(
                json.dumps({
                           "error": "Invalid message!, message must be JSON"}))
            return
        if("event" in jsonMsg):
            if(jsonMsg["event"] in self.messages_for_listening):
                self.messages_for_listening[jsonMsg["event"]](jsonMsg)

    def on_close(self):
        if self in cl:
            cl.remove(self)
        if("on_close" in self.messages_for_listening):
            message = {"event": "on_close", "message": "connection closed"}
            self.messages_for_listening["on_close"](message)

    def send(self, message):
        self.write_message(json.dumps(message))

    def message_contains_fields(self, message, *fields):
        missing = []
        for field in fields:
            if(field in message):
                continue
            else:
                missing.append(field)
        return missing

    def send_message_missing_fields_error(self, missing_fields):
        self.send({"error": "Request is missing parameters!",
                   "message": missing_fields})


class RestHandler(web.RequestHandler):
    def initialize(self, module):
        self.module = module

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def send_external_request(self, address, params, isPost=False):
        params = urllib.urlencode(params)

        # get encoded user token:
        header = {}
        token = self.get_cookie("user")
        if token is not None:
            header["user"] = token

        if isPost:
            client = tornado.httpclient.AsyncHTTPClient()
            return gen.Task(client.fetch,
                            address,
                            method="POST",
                            body=params,
                            headers=header)
        else:
            url = address + "/?" + params

            client = tornado.httpclient.AsyncHTTPClient()
            return gen.Task(client.fetch,
                            url,
                            headers=header)

    def find_plugin(self,
                    service_type,
                    service_category,
                    service_name,
                    host_address = "*"):
        return self.module.get_plugin(service_type, service_category, service_name, host_address)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:8888")
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        pass

    def post(self):
        pass
