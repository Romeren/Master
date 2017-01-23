# -*- coding: utf-8 -*-  # NOQA
import json
import lmdb
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


"""
    This module gets and sets access rights of a user.
    The information will take the following form:

    [
   { "service" : "service_name", "identifier": "someid", "permision": "read" },
  { "service" : "service_name", "identifier": "someid", "permision": "write" },
   { "service" : "service_name", "identifier": "someid", "permision": "read" },
        ...
    ]

    Not that if a permision is not present, it means that the user does
    not have the premision!

    Secondly the user cannot create permisions or update them.
    This is purely done by the module itself!
"""
# TODO(SEQURITY): validate that a given servce is in fact that service!
# this can be done with certificates or by sending a request to the service
# expecting a reply...


class Service(abstract_plugin):

    def get(self):
        # Check that user is loged in:
        user = self.get_current_user()
        reply = {"status": 400}
        if user is None:
            reply["status"] = 401
            self.write(reply)
            return

        # must have two input parameters:
        username = self.get_argument("username", "")
        service = self.get_argument("service", "")

        # validate input
        if not self.__validate_string_input(username):
            reply["message"] = "No username in request!"
            self.write(reply)
            return

        # validate input
        if not self.__validate_string_input(service):
            reply["message"] = "No service in request!"
            self.write(reply)
            return

        # Validate that the request comes from a valid service and the same
        # service that the request is about:
        # TODO(CREATE): create this!

        # check if exists:
        rights = self.__get_users_access_rights(username.lower())

        permisions = []
        
        reply["status"] = 200
        reply["username"] = username

        if rights is None or rights == "None":
            reply["permissions"] = permisions
            reply["message"] = "You have no power here, Gandalf the Gay!"
            self.write(reply)
            return

        for right in json.loads(rights):
            if right["service"] == service:
                permisions.append(right)

        reply["permissions"] = permisions
        self.write(reply)

    def post(self):
        # Check that user is loged in:
        user = self.get_current_user()
        reply = {"status": 400}
        if user is None:
            reply["status"] = 401
            self.write(reply)
            return

        # must have two input parameters:
        username = self.get_argument("username", "")
        permision = self.get_argument("permisions", "")

        # validate input
        if not self.__validate_string_input(username):
            reply["message"] = "No username in request!"
            self.write(reply)
            return

        # validate input:
        try:
            permision = json.loads(permision)
        except Exception:
            reply["message"] = "permision is not in json format!"
            self.write(reply)
            return

        if("service" not in permision or "identifier" not in permision or
           "permision" not in permision):
            reply["message"] = "permision is missing one or more fields!"
            self.write(reply)
            return

        if(not self.__validate_string_input(permision["service"]) or
           not self.__validate_string_input(permision["identifier"]) or
           not self.__validate_string_input(permision["permision"])):
            reply["message"] = "permision fields are not valid!"
            self.write(reply)
            return

        if permision["permision"] not in ["read", "write"]:
            reply["message"] = "permisions permision is invalid!"
            self.write(reply)
            return

        # check that this message comes from a valid service!
        # TODO(create): create security!

        # get users permisions:
        currentRights = self.__get_users_access_rights(username.lower())

        # update or create permisions:
        success = False
        if currentRights is None or currentRights == "None":
            # Insert permission:
            success = self.__store_users_access_rights(username.lower, [permision])   # NOQA
        else:
            # Update permisions:
            #
            # check if specific permision exists:
            currentRights = json.loads(currentRights)
            specificPerm = None
            permIndex = None
            for i in range(0, len(currentRights)):
                right = currentRights[i]
                if(right["service"] == permision["service"] and
                   right["identifier"] == permision["identifier"]):
                    specificPerm = right
                    permIndex = i
                    break

            if specificPerm is None:
                # append the new permision:
                currentRights.append(permision)
                success = self.__store_users_access_rights(username,
                                                           currentRights)
            else:
                perm = currentRights[permIndex]
                perm["permision"] = permision["permision"]
                success = self.__store_users_access_rights(username,
                                                           currentRights)

        # send response:
        if success:
            reply["status"] = 200
            reply["permisions"] = permision

        self.write(reply)

    def __validate_string_input(self, param):
        if(param is None or
           not isinstance(param, (str, bytes)) or
           param == "" or param == "None"):
            return False
        return True

    def __get_users_access_rights(self, username):
        env = lmdb.open('services/account/ownership/ownershipdb')
        with env.begin(write=False, buffers=True) as txn:
            buf = txn.get(username.encode("utf-8"))
            if buf is None:
                return None
            return bytes(buf)

    def __store_users_access_rights(self, username, permissions):
        env = lmdb.open('services/account/ownership/ownershipdb')
        with env.begin(write=True, buffers=True) as txn:
            return txn.put(str(username), json.dumps(permissions))

config = {"service_name": "account/ownership",
          "handler": Service,
          "service_type": "rest",
          "service_category": "plugin"
          }
