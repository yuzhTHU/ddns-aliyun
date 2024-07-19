#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipv4

class Ident(ipv4.IPV4):
    def get_ip():
        ident = ipv4.request.urlopen('https://ident.me').read().decode('utf-8')
        return ident