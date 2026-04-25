#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv4 import IPV4

class IP42(IPV4):
    def get_ip(self):
        ip42 = json.loads(request.urlopen('http://ip.42.pl/raw').read().decode('utf-8'))
        return ip42