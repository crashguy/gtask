import os
import sys

self_dir = os.path.abspath(os.path.join(__file__, os.pardir)) + '/'
work_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)) + '/'
if work_dir not in sys.path:
    sys.path.insert(0, work_dir)

import logging
import time
from datetime import datetime
import requests
from env import mongo_config
from gtask_db import db
from gtask_db.gpu_mission import GpuMission
from gtask_db.machine import Machine, Gpu
from collections import defaultdict

SLEEP = 15


def init_gpu():
    Gpu.drop_collection()
    machines = Machine.objects(accept_jobs__contains='gpu').all()
    for m in machines:
        try:
            r = requests.get("http://%s/gpu/info/json" % m['plugin']).json()
            for i, g in enumerate(r['Devices']):
                gpu = Gpu(machine=m, path=g['Path'], order=i)
                gpu['model'] = g['Model']
                gpu['max_power'] = g['Power']
                gpu['init_time'] = datetime.now()
                gpu.save()

            m['gpu_last_update'] = datetime.now()
            m.save()
        except Exception as e:
            logging.error('%s init failed' % m['name'])
            logging.error(e)
            raise


def update_machine():
    # offline all gpus
    all_machines = Machine.objects().all()
    for m in all_machines:
        m['available_gpus'] = []
        m.save()

    machines = Machine.objects(accept_jobs__contains='gpu').all()
    gpus = Gpu.objects().all()
    gpus_dict = defaultdict(dict)
    for gpu in gpus:
        gpus_dict[gpu['machine']['name']][gpu['order']] = gpu
    updated_machines = list()
    for m in machines:
        try:
            # m['available_gpus'] = []
            r = requests.get("http://%s/gpu/status/json" % m['plugin']).json()
            for i, g in enumerate(r['Devices']):
                _gpu = gpus_dict[m['name']][i]
                _gpu['power'] = g['Power']
                _gpu['temperature'] = g['Temperature']
                if g['Processes']:
                    _gpu['processes'] = ','.join([str(p['PID']) for p in g['Processes']])
                else:
                    m['available_gpus'].append(_gpu['path'])
                    _gpu['processes'] = ''
                _gpu['last_update'] = datetime.now()
                _gpu.save()
            start_missions = GpuMission.objects(running_machine=m['name'], status='running').all()
            for mission in start_missions:
                m['available_gpus'] = list(set(m['available_gpus']) - set(mission['running_gpu']))

            m['gpu_last_update'] = datetime.now()
            m.save()
            updated_machines.append(m)
        except Exception as e:
            logging.error(e)
            # raise
    return updated_machines


def update_mission():
    missions = GpuMission.objects(status='running').all()
    machines = Machine.objects().all()
    machine_dict = {m['name']: m for m in machines}

    for mission in missions:
        try:
            log_request = requests.get("http://%s/containers/%s/logs?stdout=1&stderr=1" % (machine_dict[mission['running_machine']]['host'], mission['running_id'][:12]))
            mission['running_log'] = log_request.text
            r = requests.get("http://%s/containers/%s/json" % (machine_dict[mission['running_machine']]['host'], mission['running_id'][:12])).json()
            mission['status'] = r['State']['Status']
            if mission['status'] != 'running':
                mission['finish_time'] = datetime.now()
        except Exception as e:
            mission['error_log'] = str(e)
        mission['update_time'] = datetime.now()
        mission.save()


def deploy_mission(machine, mission):
    post_data = {
        "Image": mission['docker'],
        "Volumes": {
            cuda_lib: {}
            for cuda_lib in machine['cuda_libs']
            },
        "Entrypoint": ["python", "-u", "entry.py",
                       mission['git_username'], mission['git_passwd'],
                       mission['repo'], mission['branch'],
                       mission['command']],
        "HostConfig": {
            "Binds": [
                         '%s:%s' % (cuda_lib, cuda_lib)
                         for cuda_lib in machine['cuda_libs']
                         ] + machine['ro_cuda_libs'],
            "Devices": [{"PathOnHost": machine['available_gpus'][i],
                         "PathInContainer": "/dev/nvidia%d" % i,
                         "CgroupPermissions": "mrw"}
                        for i in range(mission['gpu_num'])] +
                       [{"PathOnHost": dev,
                         "PathInContainer": dev,
                         "CgroupPermissions": "mrw"} for dev in machine['devices']]
        }
    }
    if mission['volumes']:
        post_data['HostConfig']['Binds'].extend([v.strip() for v in mission['volumes'].split(',')])

    create_url = 'http://' + machine['host'] + '/containers/create?name=%s' % mission['name']
    start_url = 'http://' + machine['host'] + '/containers/{}/start'
    try:
        resp = requests.post(create_url, json=post_data)
        if resp.status_code >= 400:
            raise Exception('create failed. code={}. {}'.format(resp.status_code, resp.text))
        r = resp.json()
        mission['running_id'] = r['Id']
        mission['running_machine'] = machine['name']
        mission['running_gpu'] = machine['available_gpus'][:mission['gpu_num']]
        mission['start_time'] = datetime.now()
        resp = requests.post(start_url.format(r['Id'][:12]))
        if resp.status_code >= 400:
            raise Exception('start failed. code={}. {}'.format(resp.status_code, resp.text))
        mission['status'] = 'running'
        mission['error_log'] = ''
    except Exception as e:
        mission['status'] = 'start failed'
        mission['error_log'] = str(e)
        logging.error(e)

    mission.save()


def deploy(machines):
    for machine in machines:
        rest_gpus = len(machine['available_gpus'])
        if rest_gpus == 0:
            continue
        next_job = GpuMission.objects(machine__contains=machine['name'], status='queueing').first()
        if not next_job:
            continue
        if next_job['gpu_num'] > rest_gpus:
            continue
        deploy_mission(machine, next_job)


if __name__ == '__main__':
    db.connect(mongo_config['DB'],
               host="%s:%s" % (mongo_config['host'], mongo_config['port']))
    init_gpu()
    while True:
        machines = update_machine()
        update_mission()
        deploy(machines)
        time.sleep(SLEEP)
