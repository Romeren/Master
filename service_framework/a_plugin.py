# -*- coding: utf-8 -*-  # NOQA
""" sample implementation of a plugin
"""
# from plugin_module import Plugin_module
import json
from tornado import gen
from tornado import httpclient
from tornado import web
from tornado import websocket
from urllib.parse import urlencode
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
        params = urlencode(params)

        # get encoded user token:
        header = {}
        token = self.get_cookie("user")
        if token is not None:
            header["Cookie"] = "user="+token

        if isPost:
            client = httpclient.AsyncHTTPClient()
            return gen.Task(client.fetch,
                            address,
                            method="POST",
                            body=params,
                            headers=header)
        else:
            url = address + "/?" + params

            client = httpclient.AsyncHTTPClient()
            return gen.Task(client.fetch,
                            request=url,
                            method="GET",
                            headers=header)

    def get_service_address(self,
                            service_name,
                            service_type="rest",
                            service_category="plugin",
                            host="*"):
        info = self.find_service(service_type,
                                 service_category,
                                 service_name,
                                 host)

        return self.get_service_address_from_request(info)

    def get_service_address_from_request(self, request):
        address = None
        if request is not None:
            address = "http://" + request["host_address"]
            address += ":" + str(request["port"])
            address += "/" + request["service_name"]
        return address

    def find_services(self,
                      service_type,
                      service_category,
                      service_name,
                      host_address="*"):
        return self.module.get_services(service_type,
                                        service_category,
                                        service_name,
                                        host_address)

    def find_service(self,
                     service_type,
                     service_category,
                     service_name,
                     host_address="*"):
        return self.module.get_service(service_type,
                                       service_category,
                                       service_name,
                                       host_address)

    def set_default_headers(self):
        origin = self.request.headers.get('Origin')
        # TODO(SECURITY): check origin from a list!
        if origin is None:
            self.set_header("Access-Control-Allow-Origin", "*")
        else:
            self.set_header("Access-Control-Allow-Origin", origin)
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get_basic_context(self):
        context = {}
        fields = ["javascripts", "miscellanceous"]
        context[fields[0]] = self.get_service_address(fields[0],
                                                      service_category=fields[1]  # NOQA
                                                      )
        context = self.__set_user_info(context)
        context["references"] = {}
        return context

    def get_service_reference(self,
                              service_type,
                              service_category,
                              service_name):
        return self.__get_service_ref(service_name=service_name,
                                      addr=self.get_service_address(service_name=service_name,  # NOQA
                                                                    service_type=service_type,  # NOQA
                                                                    service_category=service_category),  # NOQA
                                      error=False)

    def get_service_reference_from_request(self, request):
        return self.__get_service_ref(service_name=request["service_name"],  # NOQA
                                      addr=self.get_service_address_from_request(request),  # NOQA
                                      error=False)

    def __get_service_ref(self,
                          service_name,
                          addr,
                          error=False):
            return {
                "name": service_name.replace("_", " "),
                "service_name_js": service_name.replace("/", "\\\/"),
                "service_name": service_name,
                "address": addr,
                "hasError": error
            }

    def __set_user_info(self, context):
        user = self.get_current_user()
        context["user"] = user
        if user:
            context["loggedin"] = True
        else:
            context["loggedin"] = False
        return context

    def get(self):
        pass

    def post(self):
        pass
