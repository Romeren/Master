# -*- coding: utf-8 -*-  # NOQA
""" sample implementation of a plugin
"""
# from plugin_module import Plugin_module
import json
from tornado import gen
import tornado.httpclient
from tornado import web
from tornado import websocket
import urllib
import zmq
cl = []


class SocketHandler(websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super(websocket.WebSocketHandler, self).__init__(application,
                                                         request,
                                                         **kwargs)

    def load_external_plugin(self,
                             service_type="*",
                             service_name="*",
                             host_address="*"):
        broker_address = "localhost"
        broker_port = 5555
        # request plugin at broker:
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        bk_url = "tcp://" + broker_address + ":" + str(broker_port)
        socket.connect(bk_url)

        socket.send(json.dumps({"get_service": {
            "service_type": service_type,
            "service_name": service_name,
            "host_address": host_address
            }
            }))

        message = socket.recv()
        message = json.loads(message)
        socket.close()
        print(message)
        return message

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

    def get_external_plugin_address(self, service_name, service_type):
        message = self.load_external_plugin(service_name=service_name,
                                            service_type=service_type)
        if message["status"] != 200:
            return None

        service = message["service"]

        address = "http://" + service["hostname"] + ":"
        address += str(service["port"]) + "/"
        address += service["service_name"]
        return address

    def load_external_plugin(self,
                             service_type="*",
                             service_name="*",
                             host_address="*"):
        broker_address = "localhost"
        broker_port = 5555
        # request plugin at broker:
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        bk_url = "tcp://" + broker_address + ":" + str(broker_port)
        socket.connect(bk_url)

        socket.send(json.dumps({"get_service": {
            "service_type": service_type,
            "service_name": service_name,
            "host_address": host_address
            }
            }))

        message = socket.recv()
        message = json.loads(message)
        socket.close()
        return message

    def find_plugin(self, service_type, service_name, service_category):
        # request plugin at broker:
        topic = self.__build_topic(service_type, service_category, service_name, "*")
        clients = self.__get_matching(plugins, topic)
        try:
            service = clients.next()
        except Exception:
            return None
        return service

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

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:8888")
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        pass

    def post(self):
        pass
