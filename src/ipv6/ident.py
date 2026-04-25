#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv6 import IPV6

class Ident(IPV6):
    def get_ip(self):
        ident = request.urlopen('https://v6.ident.me').read().decode('utf-8')
        return ident