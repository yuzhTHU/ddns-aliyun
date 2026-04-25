#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from urllib import request
from .ipv4 import IPV4

class IPCN(IPV4):
    def get_ip(self):
        ipcnReq = request.Request(url=f'https://ip.cn/api/index?ip=&type=0', headers=IPV4.Headers, method='GET')
        ipcn = json.loads(request.urlopen(ipcnReq).read().decode('utf-8'))['ip']
        return ipcn