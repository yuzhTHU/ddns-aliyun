#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
from joblib import Parallel, delayed
from collections import Counter
from abc import ABC, abstractmethod

_logger = logging.getLogger(__name__)

class IPV4(ABC):
    Headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # 'Content-type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57'
    }

    @abstractmethod
    def get_ip(self) -> str:
        pass
    
    @classmethod
    def get_local_ip(cls, use_parallel=False) -> str:
        """ Get local machine's ipv4 address by all registered functions, and return the most common one. """
        
        subclasses = IPV4.__subclasses__()
        if len(subclasses) == 0:
            _logger.warning("No functions are registered for ipv4")
            return None

        def fetch_ip(subclass):
            try:
                ip = subclass().get_ip()
                _logger.info(f"[{subclass.__name__}] Get local IP: {ip}")
                return ip
            except Exception as e:
                _logger.warning(f"[{subclass.__name__}] Error occurred: {e}")
                return None

        if use_parallel:
            try:
                tasks = [delayed(fetch_ip)(subclass) for subclass in subclasses]
                workers = Parallel(n_jobs=len(subclasses), backend="threading")
                ip_list = [ip for ip in workers(tasks) if ip is not None]
            except Exception as e:
                _logger.error(f"Parallel execution failed: {e}. Falling back to sequential execution.")
                ip_list = None

        if not use_parallel or ip_list is None:
            results = [subclass().get_ip() for subclass in subclasses]
            ip_list = [ip for ip in results if ip is not None]

        if len(ip_list) == 0:
            _logger.warning("Local machine has no ipv4.")
            return None

        common_ip = Counter(ip_list).most_common(1)[0][0]
        return common_ip
    
    @classmethod
    def get_local_ip_parallel(cls) -> str:
        """ Get local machine's ipv4 address by all registered functions in parallel, and return the most common one. """
        
        subclasses = IPV4.__subclasses__()
        if len(subclasses) == 0:
            _logger.warning("No functions are registered for ipv4")
            return None

        ip_list = []

        def foo(subclass):
            try:
                ip = subclass().get_ip()
                _logger.info(f"[{subclass.__name__}] Get local IP: {ip}")
                return ip
            except Exception as e:
                _logger.warning(f"[{subclass.__name__}] Error occurred: {e}")
                return None

        tasks = [delayed(foo)(subclass) for subclass in subclasses]
        workers = Parallel(n_jobs=-1, backend="threading")
        ip_list = [ip for ip in workers(tasks) if ip is not None]

        if len(ip_list) == 0:
            _logger.warning("Local machine has no ipv4.")
            return None

        common_ip = Counter(ip_list).most_common(1)[0][0]
        return common_ip