# encoding: utf-8

import logging
import os
import sys


self_dir = os.path.abspath(os.path.join(__file__, os.pardir)) + '/'
work_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)) + '/'
if work_dir not in sys.path:
    sys.path.insert(0, work_dir)
from gtask_db.mission import Mission

from flask import Flask, request, jsonify
import flask_admin as admin
from env import mongo_config

logging.basicConfig(filename=work_dir + 'gtask_admin/log/request_mapping.log',
                    level=logging.DEBUG,
                    filemode='a',
                    format='%(asctime)s,%(levelname)s,%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Create application
app = Flask(__name__)

# Create dummy secret key so we can use sessions
app.config['SECRET_KEY'] = 'gtask_admin_for_singulariti'
app.config['MONGODB_SETTINGS'] = mongo_config


def check_params(mission, param_list):
    for p in param_list:
        if p not in mission:
            return False, p
    return True, None


@app.route('/mission/', methods=['POST'])
def create_mission():
    missions = request.json
    failed_mission = list()
    for mission in missions:
        ok, p = check_params(mission, ['job', 'name', 'docker', 'machine', 'command'])
        if ok:
            m = Mission(**mission)
            m.status = 'queueing'
            m.save()
        else:
            failed_mission.append(mission.get('name', 'unknown') + ' need arg ' + p)
    return jsonify(dict(failed_missions=failed_mission))


# Create admin
gtask_admin = admin.Admin(app, 'Tracker Admin')
