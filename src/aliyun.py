#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import json
import uuid
import hmac
import base64
import socket
import logging
import datetime
import ipaddress
from urllib import request, parse

_logger = logging.getLogger(__name__)


class Aliyun():
    Headers = {
        'Accept': 'text/json',
        'Content-type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }

    def __init__(self, access_key_id, access_key_secret):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.params = {
            'AccessKeyId': access_key_id,
            'Format':'json',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'Timestamp': datetime.datetime.utcnow().isoformat(),
            'Version': '2015-01-09',
        }

    def ddns(self, domain_name, ip, sub_domains):
        if not self.check_domain_exists(domain_name):
            raise ValueError(f"Domain [{domain_name}] not exists.")
        if ip is None or ip == '':
            raise ValueError("IP address is empty.")

        if not isinstance(sub_domains, list):
            sub_domains = [sub_domains]
        record_type = 'AAAA' if (ipaddress.ip_address(ip).version == 6) else 'A'
        for sub_domain in sub_domains:
            if (record := self.get_record(domain_name, sub_domain, record_type)) is None:
                _logger.info(f"Begin add [{sub_domain}.{domain_name}] as [{ip}].")
                self.add_record(domain_name, sub_domain, record_type, ip)
            elif record['Value'] != ip:
                _logger.info(f"Begin update [{sub_domain}.{domain_name}] from [{record['Value']}] to [{ip}].")
                self.update_record(domain_name, sub_domain, record_type, ip, record['RecordId'])
            else:
                _logger.info(f"Record [{sub_domain}.{domain_name}] is up to date.")

    def check_domain_exists(self, domain_name):
        try:
            self._get_response_data(Action='DescribeDomainInfo', DomainName=domain_name, **self.params)
            return True
        except Exception as e:
            _logger.error(f"Check domain exists failed: {[type(e)]} {e}")
            return False

    def get_record(self, domain_name, sub_domain, record_type):
        try:
            page_number = 1
            total_number = 1
            while page_number <= total_number:
                data = self._get_response_data(Action='DescribeDomainRecords', DomainName=domain_name, PageSize=100, PageNumber=1, **self.params)
                records = data['DomainRecords']['Record']
                for record in records:
                    if record['Type'] == record_type and record['RR'] == sub_domain:
                        return record
                page_number += 1
                total_number = data['TotalCount'] // data['PageSize'] + 1
            return None
        except Exception as e:
            _logger.error(f"Get record failed: {[type(e)]} {e}")
            raise Exception("Get record failed.")

    def add_record(self, domain_name, sub_domain, record_type, localIP):
        try:
            data = self._get_response_data(Action='AddDomainRecord', DomainName=domain_name, RR=sub_domain, Type=record_type, Value=localIP, **self.params)
            return data['RecordId']
        except Exception as e:
            _logger.error(f"Add record failed: {[type(e)]} {e}")
            raise Exception("Add record failed.")

    def update_record(self, domain_name, sub_domain, record_type, localIP, record_id):
        try:
            data = self._get_response_data(Action='UpdateDomainRecord', RR=sub_domain, RecordId=record_id, Type=record_type, Value=localIP, **self.params)
            return data['RecordId']
        except Exception as e:
            _logger.error(f"Update record failed: {[type(e)]} {e}")
            raise Exception("Update record failed.")

    def _get_response_data(self, **params):
        params['SignatureNonce'] = uuid.uuid1()
        params = {key: params[key] for key in sorted(params.keys())}
        params['Signature'] = self._sign(params)
        req = request.Request(url=f'https://alidns.aliyuncs.com/?{parse.urlencode(params)}', headers=self.Headers, method='GET')
        response = request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))

    def _sign(self, params):
        stringToSign = 'GET&%2F&' + parse.quote(parse.urlencode(params))
        h = hmac.new(
            (self.access_key_secret + '&').encode('utf-8'), 
            stringToSign.encode('utf-8'), 
            digestmod='sha1'
        ).digest()
        signature = base64.b64encode(h).decode('utf-8')
        return signature
