#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import json
import logging
import aliyun
from ipv4 import IPV4
from ipv6 import IPV6
from logger import setup_logging


global IPv4_cache
IPv4_cache = None
def get_ipv4():
    global IPv4_cache
    if not IPv4_cache: IPv4_cache = IPV4().get_local_ip()
    return IPv4_cache


global IPv6_cache
IPv6_cache = None
def get_ipv6():
    global IPv6_cache
    if not IPv6_cache: IPv6_cache = IPV6().get_local_ip()
    return IPv6_cache


if __name__ == '__main__':
    setup_logging()
    conf = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf.json"), "r"))
    aliyun_client = aliyun.Aliyun(conf['access_key'], conf['access_secret'])
    for domain in conf['ddns']:
        try:
            ip = get_ipv4() if not domain.get('ipv6', False) else get_ipv6()
            aliyun_client.ddns(domain['name'], ip, domain['sub_domains'])
        except Exception as e:
            logging.error(e)
            pass
