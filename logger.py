import json
import logging.config
import os

def setup_logging(default_path="logging.json",default_level=logging.INFO,env_key="LOG_CFG"):
    path = os.getenv(env_key,None) or default_path
    if os.path.exists(path):
        logging.config.dictConfig(json.load(open(path,"r")))
    else:
        logging.basicConfig(level = default_level)


if __name__ == "__main__":
    setup_logging(default_path = "logging.json")