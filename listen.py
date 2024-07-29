import os
import ssl
import json
import logging
from functools import wraps
from argparse import ArgumentParser
from flask import Flask, request, jsonify
from aliyun import Aliyun
from logger import setup_logging

parser = ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=9010)
args = parser.parse_args()

app = Flask('Aliyun-DDNS')
conf = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf.json"), "r"))
aliyun_client = Aliyun(conf['access_key'], conf['access_secret'])

def check_auth(auth):
    try:
        logging.info(f"Auth={auth}, Username={auth.username}, Password={auth.password}")
        return (auth.username == conf['listen']['username'] and 
                auth.password == conf['listen']['password'])
    except:
        return False

def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)
    resp.status_code = 401 # 否则在浏览器访问时不会提示“服务器需要验证”
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'
    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_auth(request.authorization): 
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def check_valid(sub_domain):
    if not len(sub_domain): return False
    if sub_domain.isalnum() and sub_domain[0].isalpha(): return True
    if sub_domain in ["*", "@"]: return True
    return False

@app.route('/<sub_domain>', methods=['GET'])
@requires_auth
def set_ip(sub_domain):
    if not check_valid(sub_domain): return jsonify({"message": "Server is down."}), 500
    sub_domain = sub_domain.lower()
    client_ip = request.remote_addr
    aliyun_client.init_domain(conf['listen']['name'])
    aliyun_client.ddns(conf['listen']['name'], client_ip, sub_domain)
    logging.info(f"{sub_domain}.{conf['listen']['name']} => {client_ip}")
    return jsonify({"message": f"Hello {sub_domain}, your IP address is {client_ip}"}), 200


if __name__ == '__main__':
    setup_logging()
    kwargs = dict(host='0.0.0.0', port=args.port)
    if 'ssl_cert' in conf['listen']:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.load_cert_chain(certfile=conf['listen']['ssl_cert'], keyfile=conf['listen']['ssl_key'])
        kwargs['ssl_context'] = context
    app.run(**kwargs)
