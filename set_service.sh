#!/bin/bash

cat <<EOL > /etc/systemd/system/aliyun-ddns.service
[Unit]
Description=Flask Server for Aliyun DDNS
After=network.target

[Service]
ExecStart=/usr/bin/python3 $PWD/listen.py
WorkingDirectory=$PWD
User=$USER
Group=$(id -gn)
Restart=always
Environment="LOG_CFG=logging-NAS.json"

[Install]
WantedBy=multi-user.target
EOL

systemctl daemon-reload
systemctl start aliyun-ddns
systemctl enable aliyun-ddns

echo "\033[32;1m通过 systemctl status aliyun-ddns 检查运行状态\033[0m"
systemctl status aliyun-ddns # 检查运行状态

echo "\033[32;1m通过 journalctl -u aliyun-ddns 查看日志\033[0m"
journalctl -u aliyun-ddns
