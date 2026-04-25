#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv4 import IPV4

class IpApi(IPV4):
    def get_ip(self):
        ipapi = json.loads(request.urlopen('http://ip-api.com/json').read().decode('utf-8'))['query']
        return ipapi