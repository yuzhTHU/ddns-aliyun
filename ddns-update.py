#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import dotenv
import logging
from pathlib import Path
from argparse import ArgumentParser
from src import Aliyun, IPV4, IPV6, utils

dotenv.load_dotenv()
_logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = ArgumentParser(description="Aliyun DDNS Update Script")
    parser.add_argument('--sub_domains', nargs='+', help='Sub domains to update')
    parser.add_argument('--domain_name', help='Domain name to update', default='yumeow.site')
    parser.add_argument('--ipv6', action='store_true', help='Use IPv6 address instead of IPv4')
    parser.add_argument('--parallel', action='store_true', help='Query IP address in parallel')
    parser = utils.add_minus_separated_flags(parser)
    parser = utils.add_negation_started_flags(parser)
    args = parser.parse_args()
    utils.init_logger('src')

    if args.parallel:
        ip = IPV6.get_local_ip_parallel() if args.ipv6 else IPV4.get_local_ip_parallel()
    else:
        ip = IPV4.get_local_ip() if not args.ipv6 else IPV6.get_local_ip()
    _logger.info(f"Got local IP: {ip}")

    access_key = os.getenv('ACCESS_KEY')
    access_secret = os.getenv('ACCESS_SECRET')
    aliyun_client = Aliyun(access_key, access_secret)
    aliyun_client.ddns(args.domain_name, ip, args.sub_domains)
    _logger.info(f"Updated {args.sub_domains}.{args.domain_name} => {ip}")