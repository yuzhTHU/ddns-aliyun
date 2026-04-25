#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv4 import IPV4

class Httpbin(IPV4):
    def get_ip(self):
        httpbin = json.loads(request.urlopen('http://httpbin.org/ip').read().decode('utf-8'))['origin']
        return httpbin