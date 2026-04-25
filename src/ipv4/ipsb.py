#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv4 import IPV4

class IPSB(IPV4):
    def get_ip(self):
        ipsb = json.loads(request.urlopen('https://api-ipv4.ip.sb/ip').read().decode('utf-8'))
        return ipsb