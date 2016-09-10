import os

if os.getenv("ENV_MODE") == "docker":
    DEBUG = False
    PORT = 9020
    mongo_config = {
        'DB': 'gtask',
        'connect': False,
        'host': os.getenv("MONGODB_HOST", '10.244.95.1'),
        'port': int(os.getenv("MONGODB_PORT", 6000))
    }
elif os.getenv("ENV_MODE") == "linan":
    DEBUG = True
    PORT = 9020
    mongo_config = {
        'DB': 'gtask',
        'connect': False,
        'host': 'linan.chinacloudapp.cn',
        'port': 26000
    }
else:
    DEBUG = True
    PORT = 9020
    mongo_config = {
        'connect': False,
        'DB': 'gtask',
        'host': '172.11.51.3',
        'port': 6000
        # 'host': '172.11.30.21',
    }
