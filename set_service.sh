#!/bin/bash

cp aliyun-ddns.service /etc/systemd/system/
systemctl daemon-reload
systemctl start aliyun-ddns
systemctl enable aliyun-ddns

echo "\033[32;1m通过 systemctl status aliyun-ddns 检查运行状态\033[0m"
systemctl status aliyun-ddns # 检查运行状态

echo "\033[32;1m通过 journalctl -u aliyun-ddns 查看日志\033[0m"
journalctl -u aliyun-ddns