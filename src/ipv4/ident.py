#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv4 import IPV4

class Ident(IPV4):
    def get_ip(self):
        ident = json.loads(request.urlopen('https://ident.me').read().decode('utf-8'))
        return ident