#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipv6

class JsonIp(ipv6.IPV6):
    def get_ip():
        jsonip = ipv6.json.loads(ipv6.request.urlopen('http://ipv6.jsonip.com').read().decode('utf-8'))['ip']
        return jsonip
