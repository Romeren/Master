# -*- coding: utf-8 -*-  # NOQA
import json
import lmdb
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA
from tornado import gen
from tornado.web import asynchronous
import uuid

"""
    This plugin handles getting and storing building enteties.
    The format for these entities are as following:
    {
        "entity_id": "someuuidid",
        "name": "name"
        "children": [
                {
                "name": "parentname/name"
                "children": [
                    {
                        "name": "patentname/name"
                        "children" : []
                        ....
                    },
                    ...
                ....
            ]
        }
    }

    it is worth noting that it is completely allowed to add any further
    tags, fields or metadata to the item!
"""
permision_service_address = None


class Plugin(abstract_plugin):
    def initialize(self, module):
        self.module = module
        self.service_name = "building/entity"

    @asynchronous
    @gen.engine
    def get(self):
        # ----------------------------
        # TEST:
        # Get entity:
        # curl -X GET -d 'username=USERNAME&entity=UUID' localhost:5557/building/entity  # NOQA
        # -----------------------------
        reply = {"status": 400}

        user = self.get_current_user()
        if not user:
            reply["status"] = 401
            self.write(reply)
            return

        entity = self.get_argument("entity", "")

        # validate input
        if(entity is None or
           not isinstance(entity, (str, unicode)) or
           entity == ""):
            reply["message"] = "entityid missing!"
            self.write(reply)
            return

        # validate entity_id
        isValid = self.__validate_entity_id(entity)
        if not isValid:
            reply["message"] = "entity_id is not a valid uuid"
            self.write(reply)
            return

        # validate taht user can access entity:
        future = self.__request_permision(user)
        response = yield future

        permision = self.__validate_permision(response, entity)
        if permision is None:
            reply["status"] = 401
            reply["message"] = "User does not have permisions"
            self.write(reply)
            return

        # get entity:
        success, entity = self.__get_entity(entity)
        # return result:
        if success and entity is not None:
            reply["status"] = 200
            reply["entity"] = entity

        self.write(reply)

    @asynchronous
    @gen.engine
    def post(self):
        # ----------------------------
        # TEST:
        # create new entity:
        # curl -X POST -d 'username=hest&entity={"name":"test","children":{}}' localhost:5557/building/entity  # NOQA
        # -----------------------------
        # check that user is loged in!
        reply = {"status": 400}
        user = self.get_current_user()
        if not user:
            reply = {"status": 401}
            self.write(reply)
            return

        # get input:
        entity = self.get_argument("entity", "")

        # validate input:
        if(entity is None or
           entity == ""):
            reply["message"] = "entity missing!"
            self.write(reply)
            return

        try:
            entity = json.loads(entity)
        except Exception:
            reply["message"] = "entity is not in json format!"
            self.write(reply)
            return

        # Validate entity:
        valid = self.__validate_entity(entity)
        if not valid:
            reply["message"] = "entity is invalid"
            self.write(reply)
            return

        # check if insert or update:
        if "entity_id" in entity and entity["entity_id"] != "":
            # update:
            # check id:
            isValid = self.__validate_entity_id(entity["entity_id"])
            if not isValid:
                reply["message"] = "entity_id is not a valid uuid"
                self.write(reply)
                return

            # validate taht user can access entity:
            future = self.__request_permision(user)
            response = yield future

            permision = self.__validate_permision(response, entity)

            if permision is None or permision["permision"] != "write":
                reply["status"] = 401
                reply["message"] = "User does not have rights to modify!"
                self.write(reply)
                return

            success = self.__store_entity(entity, isUpdating=True)
        else:
            # insert:
            entity["entity_id"] = str(uuid.uuid4())

            # add user permision:
            permision = {"service": self.service_name,
                         "identifier": entity["entity_id"],
                         "permision": "write"}

            # get/check address for permision_service_address plugin:
            global permision_service_address
            if permision_service_address is None:
                permision_service_address = self.get_external_plugin_address("account/ownership", "rest")  # NOQA

            # update permisions:
            param = {'username': user, 'permision': json.dumps(permision)}
            future = self.send_external_request(permision_service_address, param, isPost=True)  # NOQA
            response = yield future
            response = json.loads(response.body)

            if response["status"] != 200:
                self.write(response)
                return
            print(response)
            success = self.__store_entity(entity, isUpdating=False)

        # return result:
        if success:
            reply["status"] = 200
            reply["entity"] = entity

        self.write(reply)

    def __request_permision(self, username):
        # get/check address for permision_service_address plugin:
        global permision_service_address
        if permision_service_address is None:
            permision_service_address = self.get_external_plugin_address("account/ownership", "rest")  # NOQA

        # check permisions:
        param = {'username': username, 'service': self.service_name}

        return self.send_external_request(permision_service_address, param)  # NOQA

    def __validate_permision(self, response, identifier):
        response = json.loads(response.body)

        if response["status"] != 200:
            return None

        for perm in response["access_rights"]:
            if perm["identifier"] == identifier:
                return perm
        return None

    def __validate_entity_id(self, entity_id):
        try:
            uuid.UUID(entity_id)
            return True
        except Exception:
            return False

    def __validate_entity(self, entity):
        if("name" in entity and entity["name"] is not None and
           isinstance(entity["name"], (str, unicode)) and
           entity["name"] != "" and "children" in entity and
           entity["children"] is not None):
            isValid = True
            for child in entity["children"]:
                isValid = self.__validate_entity(child)
                if not isValid:
                    break
            return isValid
        else:
            return False

    def __store_entity(self, entity, isUpdating):
        env = lmdb.open('services/building/entity/entitydb')
        with env.begin(write=True, buffers=True) as txn:
            return txn.put(str(entity["entity_id"]),
                           json.dumps(entity),
                           overwrite=isUpdating)

    def __get_entity(self, entity):
        env = lmdb.open('services/building/entity/entitydb')
        with env.begin(write=False, buffers=True) as txn:
            buf = txn.get(str(entity))
            buf_copy = bytes(buf)
            if buf_copy is not None:
                return True, buf_copy
            else:
                return False, None

config = {"service_name": "building/entity",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "plugin"
          }
