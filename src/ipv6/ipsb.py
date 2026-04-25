#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv6 import IPV6

class IPSB(IPV6):
    def get_ip(self):
        ipsb = request.urlopen('https://api-ipv6.ip.sb/ip').read().decode('utf-8')
        return ipsb