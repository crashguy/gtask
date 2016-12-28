# encoding: utf-8

import logging
import os
import sys

self_dir = os.path.abspath(os.path.join(__file__, os.pardir)) + '/'
work_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)) + '/'
if work_dir not in sys.path:
    sys.path.insert(0, work_dir)
from gtask_db.machine import Machine
from gtask_db.cpu_mission import Mission
from gtask_db.gpu_mission import GpuMission, GpuMissionConfig
from flask import Flask, request, jsonify, redirect, render_template
import flask_admin as admin
from env import mongo_config
from gtask_admin.views.views import MyHomeView
from util.util import get_config
import requests
from datetime import datetime

logging.basicConfig(level=logging.DEBUG,
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


@app.route('/gpu_task/<string:task_name>/log/')
def gpu_task_log(task_name):
    gpu_mission = GpuMission.objects(name=task_name).first()
    if not gpu_mission:
        return "no gpu_mission named {}".format(task_name)
    else:
        _log = gpu_mission['running_log']
        if gpu_mission['pre_logs']:
            _log = gpu_mission['pre_logs'] + _log
        return render_template("logs.html", task_name=task_name,
                               content=_log)


# edit config page
@app.route('/load_config/', methods=['POST'])
def config_edit():
    gpu_mission_name = request.form['gpu_mission_name']
    repo = request.form['repo']
    branch = request.form['branch']
    config = GpuMissionConfig.objects(gpu_mission_name=gpu_mission_name).first()
    if config:
        return jsonify(msg='config exists already, id={}'.format(config.id),
                       url='/admin/gpumission/edit/?id={}'.format(config.id))

    config = GpuMissionConfig(gpu_mission_name=gpu_mission_name,
                              content=get_config(repo, branch, 'speech/config.py'),
                              disk_path='/zfs/octp/configs/{}_config.py'.format(gpu_mission_name))
    if config['content']:
        config.save()
        return jsonify(msg='load config completed', url='/admin/gpumission/edit/?id={}'.format(config.id))
    else:
        return jsonify(msg='load config failed')


# restart cpud/gpud
@app.route("/restart/<machine_name>/<container_name>/", methods=['POST', 'GET'])
def restart_daemon(machine_name, container_name):
    machine = Machine.objects(name=machine_name).first()
    if not machine:
        return jsonify({"code": 404, "msg": "do not find machine %s" % machine_name})
    r = requests.post("http://{}/containers/{}/restart?t=5".format(machine['host'], container_name))
    return jsonify({"code": r.status_code})


# stop gpu tasks
@app.route("/stop/<machine_name>/<container_name>/", methods=['POST', 'GET'])
def stop_daemon(machine_name, container_name):
    machine = Machine.objects(name=machine_name).first()
    if not machine:
        return jsonify({"code": 404, "msg": "do not find machine %s" % machine_name})
    gpu_mission = GpuMission.objects(name=container_name).first()
    if not gpu_mission:
        return jsonify({"code": 404, "msg": "do not find gpu mission %s" % container_name})
    r = requests.post("http://{}/containers/{}/stop".format(machine['host'], container_name))
    if r.status_code < 400:
        gpu_mission['status'] = 'manual_aborted'
        gpu_mission['update_time'] = datetime.now()
        gpu_mission['finish_time'] = datetime.now()
        gpu_mission['pre_logs'] += gpu_mission['running_log'] + '\n' + '-'*50 + '\n'*2
        gpu_mission['running_log'] = ''
        gpu_mission.save()
    return jsonify({"code": r.status_code})


# Create admin
gtask_admin = admin.Admin(app, 'Tracker Admin', index_view=MyHomeView())
