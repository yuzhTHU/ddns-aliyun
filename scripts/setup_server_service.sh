#!/bin/bash

CURRENT_USER=$USER
CURRENT_GROUP=$(id -gn)
CURRENT_DIR=$PWD
SERVICE_PATH="/etc/systemd/system/aliyun-ddns-server.service"

# 使用 sudo tee 解决 /etc/systemd/system/ 的写入权限问题
cat <<EOL | sudo tee $SERVICE_PATH > /dev/null
[Unit]
Description=FastAPI Server for Aliyun DDNS
After=network.target

[Service]
ExecStart=/usr/bin/python3 $CURRENT_DIR/ddns-server.py
WorkingDirectory=$CURRENT_DIR
User=$CURRENT_USER
Group=$CURRENT_GROUP
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# 重新加载 systemd 并启动服务
sudo systemctl daemon-reload
sudo systemctl enable aliyun-ddns-server
sudo systemctl start aliyun-ddns-server

echo -e "\033[32;1m通过 systemctl status aliyun-ddns-server 检查运行状态\033[0m"
systemctl status aliyun-ddns-server --no-pager

echo -e "\033[32;1m通过 journalctl -u aliyun-ddns-server -f 查看实时日志\033[0m"