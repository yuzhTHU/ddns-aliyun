#!/usr/bin/python
# -*- coding: UTF-8 -*-
from urllib import request, parse
import hmac, datetime, uuid, base64
import json, os, logging, socket
import logger
import ipaddress


Headers = {
    'Accept': 'text/json',
    'Content-type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}


class Aliyun():
    def __init__(self, access_key_id, access_key_secret):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.params = {
            'AccessKeyId': self.access_key_id,
            'Format':'json',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'Timestamp': datetime.datetime.utcnow().isoformat(),
            'Version': '2015-01-09',
        }

    
    def ddns(self, domain_name, ip, sub_domains):
        assert self.check_domain_exists(domain_name), f"Domain [{domain_name}] not exists."
        assert ip is not None and ip != '', "IP address is empty."
        assert socket.has_dualstack_ipv6 or (ipaddress.ip_address(ip).version != 6), "Local machine has not ipv6."
        if type(sub_domains) is not list:
            sub_domains = [sub_domains]
        
        record_type = 'AAAA' if (ipaddress.ip_address(ip).version == 6) else 'A'
        for sub_domain in sub_domains:
            record = self.get_record(domain_name, sub_domain, record_type)
            if record is None:
                logging.info(f"Begin add [{sub_domain}.{domain_name}] as [{ip}].")
                self.add_record(domain_name, sub_domain, record_type, ip)
            elif record['value'] != ip:
                logging.info(f"Begin update [{sub_domain}.{domain_name}] from [{record['value']}] to [{ip}].")
                self.update_record(domain_name, sub_domain, record_type, ip, record['RecordId'])


    def check_domain_exists(self, domain_name):
        try:
            self._get_response_data(Action='DescribeDomainInfo', DomainName=domain_name, **self.params)
            return True
        except Exception as e:
            logging.error(e)
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
            logging.error(e)
            raise Exception("Get record failed.")


    def add_record(self, domain_name, sub_domain, record_type, localIP):
        try:
            data = self._get_response_data(Action='AddDomainRecord', DomainName=domain_name, RR=sub_domain, Type=record_type, Value=localIP, **self.params)
            return data['RecordId']
        except Exception as e:
            logging.error(e)
            raise Exception("Add record failed.")


    def update_record(self, domain_name, sub_domain, record_type, localIP, record_id):
        try:
            data = self._get_response_data(Action='UpdateDomainRecord', RR=sub_domain, RecordId=record_id, Type=record_type, Value=localIP, **self.params)
            return data['RecordId']
        except Exception as e:
            logging.error(e)
            raise Exception("Update record failed.")


    def _get_response_data(self, **params):
        params['SignatureNonce'] = uuid.uuid1()
        params = self._sort_dict(params)
        params['Signature'] = self._sign(params)
        req = request.Request(url=f'https://alidns.aliyuncs.com/?{parse.urlencode(params)}', headers=Headers, method='GET')
        response = request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))


    def _sort_dict(self, dic):
        return {key: dic[key] for key in sorted(dic.keys())}


    def _sign(self, params):
        stringToSign = 'GET&%2F&' + parse.quote(parse.urlencode(params))
        h = hmac.new((self.access_key_secret+'&').encode('utf-8'), stringToSign.encode('utf-8'), digestmod='sha1').digest()
        signature = base64.b64encode(h).decode('utf-8')
        return signature
