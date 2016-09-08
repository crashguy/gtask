import os

if os.getenv("ENV_MODE") == "docker":
    DEBUG = False
    PORT = 9020
    mongo_config = {
        'DB': 'gtask',
        'connect': False,
        'host': os.getenv("MONGODB_HOST"),
        'port': int(os.getenv("MONGODB_PORT"))
    }
elif os.getenv("ENV_MODE") == "produce":
    DEBUG = False
    PORT = 9020
    mongo_config = {
        'DB': 'gtask',
        'connect': False,
        # 'host': 'linan.chinacloudapp.cn',
        # 'port': 26000
    }
else:
    DEBUG = True
    PORT = 9020
    mongo_config = {
        'connect': False,
        'DB': 'gtask',
        'host': 'linan.chinacloudapp.cn',
        'port': 26000
        # 'host': '172.11.30.21',
    }
