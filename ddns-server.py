import os
import json
import dotenv
import uvicorn
import secrets
import logging
from argparse import ArgumentParser
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from src import Aliyun, utils

dotenv.load_dotenv()
_logger = logging.getLogger(__name__)

args = None
app = FastAPI(title="Aliyun-DDNS", docs_url=None, redoc_url=None)
security = HTTPBasic()

def check_auth(credentials: HTTPBasicCredentials):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("DDNS_SERVER_USERNAME"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("DDNS_SERVER_PASSWORD"))
    return correct_username and correct_password

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if not check_auth(credentials):
        _logger.info(f"Invalid Username={credentials.username} and Password={credentials.password}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticate.",
            headers={"WWW-Authenticate": 'Basic realm="Example"'},
        )

def check_valid(sub_domain: str) -> bool:
    if not len(sub_domain): return False
    if sub_domain.isalnum() and sub_domain[0].isalpha(): return True
    if sub_domain.removeprefix('*.').isalnum() and sub_domain.removeprefix('*.').isalnum(): return True
    if sub_domain in ["*", "@"]: return True
    return False

@app.get("/update/{sub_domain}")
def set_ip(sub_domain: str, request: Request, credentials: HTTPBasicCredentials = Depends(authenticate)):
    if not check_valid(sub_domain):
        return JSONResponse(content={"message": "Server is down."}, status_code=500)
    sub_domain = sub_domain.lower()
    client_ip = request.client.host
    access_key = os.getenv('ACCESS_KEY')
    access_secret = os.getenv('ACCESS_SECRET')
    aliyun_client = Aliyun(access_key, access_secret)
    aliyun_client.ddns(args.domain_name, client_ip, sub_domain)
    _logger.info(f"Updated {sub_domain}.{args.domain_name} => {client_ip}")
    return {"message": f"Hello {sub_domain}, your IP address is {client_ip}"}


@app.get("/docs", include_in_schema=False)
async def get_protected_docs(username: str = Depends(authenticate)):
    """受保护的 Swagger 文档路由"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(username: str = Depends(authenticate)):
    """受保护的 OpenAPI 架构定义（JSON文件）"""
    return get_openapi(title=app.title, version="1.0.0", routes=app.routes)


if __name__ == '__main__':
    parser = ArgumentParser(description="Aliyun DDNS Server")
    parser.add_argument('--domain_name', help='Domain name to update', default='yumeow.site')
    parser.add_argument('--listen', help='Host to listen on', default='0.0.0.0')
    parser.add_argument('--port', help='Port to listen on', default=3250, type=int)
    parser.add_argument('--ssl_cert', help='Path to SSL certificate file', default='ssl/ddns.crt')
    parser.add_argument('--ssl_key', help='Path to SSL key file', default='ssl/ddns.key')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser = utils.add_minus_separated_flags(parser)
    parser = utils.add_negation_started_flags(parser)
    args = parser.parse_args()

    utils.init_logger(
        package_name='src', 
        log_file='./logs/ddns-server.log',
        info_level='debug' if args.debug else 'info',
    )
    
    kwargs = {"host": args.listen, "port": args.port}
    if args.ssl_cert and args.ssl_key:
        kwargs['ssl_certfile'] = args.ssl_cert
        kwargs['ssl_keyfile'] = args.ssl_key
    elif args.ssl_cert or args.ssl_key:
        _logger.warning("Both ssl_cert and ssl_key must be provided for SSL. Starting without SSL.")
    else:
        _logger.info("Starting without SSL.")

    uvicorn.run(app, **kwargs)
