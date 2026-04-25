#!/bin/bash

# 1. 获取本机 hostname 并转为小写
CURRENT_DIR=$PWD
DEFAULT_HOSTNAME=$(hostname | tr '[:upper:]' '[:lower:]')

# 2. 交互确认
echo "------------------------------------------"
read -p "请输入 Subdomain 识别名 [默认: $DEFAULT_HOSTNAME]: " USER_HOSTNAME
USER_HOSTNAME=${USER_HOSTNAME:-$DEFAULT_HOSTNAME}
echo "确认使用: $USER_HOSTNAME"
echo "------------------------------------------"

# 3. 构造要原样写入的内容
# 使用单引号包裹 HEREDOC 防止 Shell 在此时解析 $((...))
NEW_CRON_BLOCK=$(cat <<EOF
# >>> [ALIYUN_DDNS_BEGIN]
# 每半小时执行（含 1~15 分钟随机延迟）
0,30 * * * * /bin/bash -c 'sleep \$((RANDOM % 841 + 60)) && python $CURRENT_DIR/ddns-update.py --subdomains $USER_HOSTNAME \\*.$USER_HOSTNAME'

# 开机即时执行（无需延迟）
@reboot /bin/bash -c 'python $CURRENT_DIR/ddns-update.py --subdomains $USER_HOSTNAME \\*.$USER_HOSTNAME'
# <<< [ALIYUN_DDNS_END]
EOF
)

# 4. 写入 crontab
# 逻辑：读取现有配置 -> 删除旧的标记块 -> 追加新块 -> 重新导入
(crontab -l 2>/dev/null | sed '/# >>> \[ALIYUN_DDNS_BEGIN\]/,/# <<< \[ALIYUN_DDNS_END\]/d'; echo "$NEW_CRON_BLOCK") | crontab -

echo "✅ 指令已写入 crontab。"
echo "执行 'crontab -l' 检查格式是否正确。"
echo "------------------------------------------"
crontab -l
echo "------------------------------------------"
