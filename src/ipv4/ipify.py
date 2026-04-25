#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv4 import IPV4

class IPIFY(IPV4):
    def get_ip(self):
        ipify = json.loads(request.urlopen('https://api.ipify.org/?format=json').read().decode('utf-8'))['ip']
        return ipify
