#!/usr/bin/env python
import inspect
import json
import requests
from functools import wraps
from base import config

class RPC(object):
    def __init__(self):
        self.rpc_host = config.RPC["host"]
        self.rpc_port = config.RPC["port"]
        self.rpc_user = config.RPC["user"]
        self.rpc_pass = config.RPC["pass"]
        self.url = 'http://' + self.rpc_host + ':' + self.rpc_port
        self.headers = {'content-type': 'application/json'}

    def make_call(self, *args):
        if len(args) < 1:
            args = []
        if not len(inspect.stack()) >= 1:
            raise Exception("Weird stack?")
        #print("Calling '%s' with: %s" % (inspect.stack()[1][3], args))
        payload = json.dumps({"method": inspect.stack()[1][3], "params": args, "jsonrpc": "2.0"})
        response = requests.get(self.url, headers=self.headers, data=payload, auth=(self.rpc_user, self.rpc_pass))
        #print("%s as %s with %s" % (self.url, self.rpc_user, self.rpc_pass))
        #print("Got: %s" % (response.text,))
        return response.json()['result']

    def listtransactions(self, params, count):
        return self.make_call(params, count)

    def getconnectioncount(self):
        return self.make_call()

    def getinfo(self):
        return self.make_call()

    def validateaddress(self, params):
        return self.make_call(params)

    def getaccountaddress(self, account):
        return self.make_call(account)

    def getbalance(self, account):
        return self.make_call(account)

    def sendfrom(self, account, address, amount):
        return self.make_call(account, address, amount)

    def sendmany(self, account, payments):
        return self.make_call(account, payments)

call = RPC()