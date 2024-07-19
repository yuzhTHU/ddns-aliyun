#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipv4

class Httpbin(ipv4.IPV4):
    def get_ip():
        httpbin = ipv4.json.loads(ipv4.request.urlopen('http://httpbin.org/ip').read().decode('utf-8'))['origin']
        return httpbin