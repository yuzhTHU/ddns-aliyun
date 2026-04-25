#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv6 import IPV6

class JsonIp(IPV6):
    def get_ip(self):
        jsonip = json.loads(request.urlopen('http://ipv6.jsonip.com').read().decode('utf-8'))['ip']
        return jsonip
