# -*- coding: utf-8 -*-  # NOQA
import lmdb
from service_framework.a_plugin import RestHandler as abstract_plugin  # NOQA


class Plugin(abstract_plugin):

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        reply = {"status": 400}

        print("STORE_USER_INPUT", username, password)
        # validate input
        if(username is None or
           not isinstance(username, (str, unicode)) or
           username == "" or
           password is None or
           not isinstance(password, (str, unicode)) or
           password == ""):
            reply["message"] = "Username or password missing!"
            self.write(reply)
            return

        # store user in db:
        success = self.__store_user_in_db(username.lower(), password)

        # return result:
        if success:
            reply["status"] = 200
            reply["username"] = username

        self.write(reply)

    def __store_user_in_db(self, username, password):
        env = lmdb.open('services/account/basic_functionality/userdb')
        with env.begin(write=True, buffers=True) as txn:
            buf = txn.get(str(username))
            if buf is None:
                txn.put(str(username), str(password))
                return True
            else:
                return False


config = {"service_name": "account/basic/store_user",
          "handler": Plugin,
          "service_type": "rest",
          "service_category": "plugin"
          }
