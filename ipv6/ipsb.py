#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipv6

class IPSB(ipv6.IPV6):
    def get_ip():
        ipsb = ipv6.request.urlopen('https://api-ipv6.ip.sb/ip').read().decode('utf-8')
        return ipsb