#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json, os, logging, socket
import aliyun
import logger
from ipv4 import IPV4
from ipv6 import IPV6


def init_domain(aliyun_client:aliyun.Aliyun, domain:dict):
    if not aliyun_client.check_domain_exists(domain['name']):
        aliyun_client.create_domain(domain['name'])


def ddns(aliyun_client:aliyun.Aliyun, domain:dict):
    record_type = 'AAAA' if domain.get('ipv6', False) else 'A'
    if record_type == 'AAAA' and socket.has_dualstack_ipv6 == False:
        logging.error(f"Local machine has not ipv6.")
        return
    
    ip = get_locat_ip(domain)
    if ip is None or ip == '': return
    
    for sub_domain in domain['sub_domains']:
        record_value = aliyun_client.get_record_value(domain['name'], sub_domain, record_type)
        if record_value == 0:
            aliyun_client.add_record(domain['name'], sub_domain, record_type, ip)
        elif record_value != ip:
            logging.info(f"Begin update [{sub_domain}.{domain['name']}].")
            record_id = aliyun_client.get_record_id(domain['name'], sub_domain, record_type)
            aliyun_client.record_ddns(record_id, sub_domain, record_type, ip)


def get_locat_ip(domain):
    if domain.get('ipv6', False):
        return get_ipv6()
    else:
        return get_ipv4()


global IPv4_cache
IPv4_cache = ''
def get_ipv4():
    global IPv4_cache
    if IPv4_cache.strip() == '':
        IPv4_cache = IPV4().get_local_ip()
    return IPv4_cache


global IPv6_cache
IPv6_cache = ''
def get_ipv6():
    global IPv6_cache
    if IPv6_cache.strip() == '':
        IPv6_cache = IPV6().get_local_ip()
    return IPv6_cache


if __name__ == '__main__':
    try:
        logger.setup_logging()
        conf = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf.json"), "r"))
        Domains = conf['domains']
        access_key = conf['access_key']
        access_secret = conf['access_secret']
        aliyun_client = aliyun.Aliyun(access_key, access_secret)
        for domain in Domains:
            init_domain(aliyun_client, domain)
            ddns(aliyun_client, domain)
    except Exception as e:
        logging.error(e)
        pass
