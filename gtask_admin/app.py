# encoding: utf-8

import logging
import os
import sys

self_dir = os.path.abspath(os.path.join(__file__, os.pardir)) + '/'
work_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)) + '/'
if work_dir not in sys.path:
    sys.path.insert(0, work_dir)
from gtask_db.cpu_mission import Mission
from gtask_db.gpu_mission import GpuMission
from flask import Flask, request, jsonify, redirect, render_template
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


@app.route('/')
def index():
    return redirect('/admin/machine/')

#.replace("\00\00\00\00\00\00", "\n")
@app.route('/gpu_task/<string:task_name>/log/')
def gpu_task_log(task_name):
    gpu_mission = GpuMission.objects(name=task_name).first()
    if not gpu_mission:
        return "no gpu_mission named {}".format(task_name)
    else:
        return render_template("logs.html", task_name=task_name,
                               content=gpu_mission['running_log'])

# Create admin
gtask_admin = admin.Admin(app, 'Tracker Admin')
