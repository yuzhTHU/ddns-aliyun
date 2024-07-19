#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipv4

class JsonIp(ipv4.IPV4):
    def get_ip():
        jsonip = ipv4.json.loads(ipv4.request.urlopen('http://ipv4.jsonip.com').read().decode('utf-8'))['ip']
        return jsonip