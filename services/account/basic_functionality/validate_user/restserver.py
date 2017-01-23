# -*- coding: utf-8 -*-  # NOQA
import lmdb
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Plugin(abstract_plugin):

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        reply = {"status": 400}

        # validate input
        if(username is None or
           not isinstance(username, (str, bytes)) or
           username == "" or
           password is None or
           not isinstance(password, (str, bytes)) or
           password == ""):
            reply["message"] = "Username or password missing!"
            self.write(reply)
            return

        # validate user in db:
        success = self.__check_user(username.lower(), password)
        # return result:
        if success:
            reply["status"] = 200
            reply["username"] = username

        self.write(reply)

    def __check_user(self, username, password):
        env = lmdb.open('services/account/basic_functionality/userdb')
        with env.begin(write=False, buffers=True) as txn:
            buf = txn.get(username.encode("utf-8"))
            if bytes(buf).decode("utf-8") == str(password):
                return True
            else:
                return False

config = {"service_name": "account/basic/validate_user",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "plugin"
          }
