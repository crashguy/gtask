# from flask_mongoengine import MongoEngine
# import mongoengine
# from env import mongo_config
#
# db = MongoEngine()

import mongoengine
from env import mongo_config

db = mongoengine
mongoengine.connect(mongo_config['DB'],
                    host="%s:%s" % (mongo_config['host'], mongo_config['port']))
