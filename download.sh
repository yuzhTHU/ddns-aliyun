download_from=$1

wget http://$download_from:8000/conf-demo.json -O ./conf.json
sed -i "s/<SUBNAME>/$(uname -n)/" conf.json

mkdir -p ssl
wget http://$download_from:8000/ssl/ddns.crt -O ssl/ddns.crt
wget http://$download_from:8000/ssl/ddns.key -O ssl/ddns.key
