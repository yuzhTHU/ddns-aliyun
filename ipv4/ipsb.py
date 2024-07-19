#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipv4

class IPSB(ipv4.IPV4):
    def get_ip():
        ipsb = ipv4.request.urlopen('https://api-ipv4.ip.sb/ip').read().decode('utf-8')
        return ipsb