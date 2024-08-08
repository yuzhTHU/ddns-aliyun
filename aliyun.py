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

CommonParams = {
    'Format':'json',
    'SignatureMethod': 'HMAC-SHA1',
    'SignatureVersion': '1.0',
    'Timestamp': datetime.datetime.utcnow().isoformat(),
    'Version': '2015-01-09',
}

class Aliyun():
    def __init__(self, access_key_id, access_key_secret):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    
    def ddns(self, domain_name, ip, sub_domains):
        if ip is None or ip == '':
            raise Exception("Empty ip.")
        ipv6 = (ipaddress.ip_address(ip).version == 6)
        if ipv6 and socket.has_dualstack_ipv6 == False:
            raise Exception("Local machine has not ipv6.")
        if type(sub_domains) is not list:
            sub_domains = [sub_domains]
        
        record_type = 'AAAA' if ipv6 else 'A'
        for sub_domain in sub_domains:
            record_value = self.get_record_value(domain_name, sub_domain, record_type)
            if record_value == 0:
                self.add_record(domain_name, sub_domain, record_type, ip)
            elif record_value != ip:
                logging.info(f"Begin update [{sub_domain}.{domain_name}].")
                record_id = self.get_record_id(domain_name, sub_domain, record_type)
                self.record_ddns(record_id, sub_domain, record_type, ip)


    def check_domain_exists(self, domain_name):
        CommonParams['AccessKeyId'] = self.access_key_id
        CommonParams['Action'] = 'DescribeDomainInfo'
        CommonParams['DomainName'] = domain_name
        try:
            self._get_response_data(CommonParams)
            return True
        except Exception as e:
            logging.error(e)
            return False


    def get_record_value(self, domain_name, sub_domain, record_type):
        CommonParams['AccessKeyId'] = self.access_key_id
        CommonParams['Action'] = 'DescribeDomainRecords'
        CommonParams['DomainName'] = domain_name
        try:
            data = self._get_response_data(CommonParams)
            records = data['DomainRecords']['Record']
            for record in records:
                if record['Type'] == record_type and record['RR'] == sub_domain:
                    logging.info(f"Sub_Domain [{sub_domain}] hostIP is {record['Value']}")
                    return record['Value']
            return 0
        except Exception as e:
            logging.error(e)
            return 0


    def get_record_id(self, domain_name, sub_domain, record_type):
        CommonParams['AccessKeyId'] = self.access_key_id
        CommonParams['Action'] = 'DescribeDomainRecords'
        CommonParams['DomainName'] = domain_name
        try:
            data = self._get_response_data(CommonParams)
            records = data['DomainRecords']['Record']
            for record in records:
                if record['Type'] == record_type and record['RR'] == sub_domain:
                    return record['RecordId']
            return 0
        except Exception as e:
            logging.error(e)
            return 0


    def add_record(self, domain_name, sub_domain, record_type, localIP):
        CommonParams['AccessKeyId'] = self.access_key_id
        CommonParams['Action'] = 'AddDomainRecord'
        CommonParams['DomainName'] = domain_name
        CommonParams['RR'] = sub_domain
        CommonParams['Type'] = record_type
        CommonParams['Value'] = localIP

        try:
            data = self._get_response_data(CommonParams)
            return data['RecordId']
        except Exception as e:
            logging.error(e)
            return 0


    def record_ddns(self, record_id, sub_domain, record_type, localIP):
        CommonParams['AccessKeyId'] = self.access_key_id
        CommonParams['Action'] = 'UpdateDomainRecord'
        CommonParams['RR'] = sub_domain
        CommonParams['RecordId'] = record_id
        CommonParams['Type'] = record_type
        CommonParams['Value'] = localIP

        try:
            data = self._get_response_data(CommonParams)
            return data['RecordId']
        except Exception as e:
            logging.error(e)
            return 0


    def _get_response_data(self, params):
        CommonParams['SignatureNonce'] = uuid.uuid1()
        params = self._sort_dict(params)

        params['Signature'] = self._sign(params)
        req = request.Request(url=f'https://alidns.aliyuncs.com/?{parse.urlencode(params)}', headers=Headers, method='GET')
        response = request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))


    def _sort_dict(self, dic):
        result = {}
        for key in sorted(dic.keys()):
            result[key] = dic[key]
        return result


    def _sign(self, params):
        stringToSign = 'GET&%2F&' + parse.quote(parse.urlencode(params))
        h = hmac.new((self.access_key_secret+'&').encode('utf-8'), stringToSign.encode('utf-8'), digestmod='sha1').digest()
        signature = base64.b64encode(h).decode('utf-8')
        return signature
