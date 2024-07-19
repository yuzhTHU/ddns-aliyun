from flask import Flask, request, jsonify
from functools import wraps
import logger
import json, os, logging
from aliyun import Aliyun

app = Flask('Aliyun-DDNS')
conf = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf.json"), "r"))
aliyun_client = Aliyun(conf['access_key'], conf['access_secret'])

def check_auth(auth):
    try:
        return (auth.username == conf['listen']['username'] and 
                auth.password == conf['listen']['password'])
    except:
        return False

def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)
    resp.status_code = 500 # 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'
    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_auth(request.authorization): 
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/<subdomain>', methods=['GET'])
@requires_auth
def set_ip(sub_domain):
    client_ip = request.remote_addr
    aliyun_client.init_domain(conf['listen']['name'])
    aliyun_client.ddns(conf['listen']['name'], client_ip, sub_domain)
    logging.info(f"Client IP: {client_ip}, Sub_domain: {sub_domain}")
    return jsonify({"message": f"Received request for {sub_domain} from {client_ip}"}), 200


if __name__ == '__main__':
    logger.setup_logging()
    app.run(host='0.0.0.0', port=9010)
