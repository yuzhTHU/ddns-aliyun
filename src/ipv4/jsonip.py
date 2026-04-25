#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv4 import IPV4

class JsonIp(IPV4):
    def get_ip(self):
        jsonip = json.loads(request.urlopen('http://ipv4.jsonip.com').read().decode('utf-8'))['ip']
        return jsonip