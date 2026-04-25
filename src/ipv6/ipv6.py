#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
from collections import Counter
from abc import ABC, abstractmethod

_logger = logging.getLogger(__name__)

class IPV6(ABC):
    Headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # 'Content-type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57'
    }

    @abstractmethod
    def get_ip(self) -> str:
        pass
    
    @classmethod
    def get_local_ip(cls) -> str:
        """ Get local machine's ipv6 address by all registered functions, and return the most common one. """
        subclasses = IPV6.__subclasses__()
        if len(subclasses) == 0:
            _logger.warning("No functions are registered for ipv6")
            return None

        ip_list = []
        for subclass in subclasses:
            try:
                ip_list.append(ip := subclass().get_ip())
                _logger.info(f"[{subclass.__name__}] Get local IPv6: {ip}")
            except Exception as e:
                _logger.warning(f"[{subclass.__name__}] Error occurred: {e}")
                pass

        if len(ip_list) == 0:
            _logger.warning("Local machine has no ipv6.")
            return None

        common_ip = Counter(ip_list).most_common(1)[0][0]
        return common_ip