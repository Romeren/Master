# -*- coding: utf-8 -*-  # NOQA
import lmdb
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Plugin(abstract_plugin):

    def post(self):
        username = self.get_argument("username", "")

        reply = {"status": 400}

        # validate input
        if(username is None or
           not isinstance(username, (str, unicode)) or
           username == ""):
            reply["message"] = "No username in request!"
            self.write(reply)
            return

        # check if exists:
        exists = self.__check_username(username.lower())

        # return result
        if exists:
            reply["status"] = 200
            reply["username"] = username
        self.write(reply)

    def __check_username(self, username):
        env = lmdb.open('services/account/basic_functionality/userdb')
        with env.begin(write=False, buffers=True) as txn:
            buf = txn.get(str(username))
            if buf is None:
                return False
            else:
                return True


config = {"service_name": "account/basic/check_username",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "plugin"
          }
