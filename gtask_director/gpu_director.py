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
from gtask_db.gpu_task import GpuTask, GpuTaskLog
from gtask_db.machine import Machine, Gpu
from collections import defaultdict

SLEEP = 15

available_ports = [
    6006, 6007, 6008, 6009
]


def check_image_exist(machine, image_name):
    try:
        r = requests.get("http://%s/images/json?filter=%s" % (machine['plugin'], image_name)).json()
        if r:
            logging.info("%s has image %s" % (machine['name'], image_name))
            return True
        else:
            logging.info("%s does not have image %s" % (machine['name'], image_name))
            return False

    except Exception as e:
        logging.error('%s check image %s failed' % (machine['name'], image_name))
        logging.error(e)
        raise


def download_image(machine, image_name):
    try:
        requests.post("http://%s/images/create?fromImage=%s" % (
            machine['plugin'], image_name))
        logging.info('%s start to download image %s failed' % (machine['name'], image_name))

    except Exception as e:
        logging.error('%s download image %s failed' % (machine['name'], image_name))
        logging.error(e)
        raise


def init_gpu(machines):
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
    # offline not available gpus
    all_machines = Machine.objects(accept_jobs__not__contains='gpu').all()
    for m in all_machines:
        m['available_gpus'] = []
        m.save()

    machines = Machine.objects(accept_jobs__contains='gpu').all()
    gpus = Gpu.objects().all()
    gpus_dict = defaultdict(dict)
    for gpu in gpus:
        gpus_dict[gpu['machine']['name']][gpu['order']] = gpu
    not_init_machines = [m for m in machines if m['name'] not in gpus_dict]
    init_gpu(not_init_machines)

    updated_machines = list()
    for m in machines:
        try:
            m['available_gpus'] = []
            m['ports'] = available_ports
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
            start_tasks = GpuTask.objects(running_machine=m['name'], status='running').all()
            for task in start_tasks:
                m['available_gpus'] = list(set(m['available_gpus']) - set(task['running_gpu']))
                m['ports'] = list(set(m['ports']) - {task['mount_port']})

            m['gpu_last_update'] = datetime.now()
            m.save()
            updated_machines.append(m)
        except Exception as e:
            logging.error(e)
            # raise
    return updated_machines


def check_result(task, task_log):
    finish_tag = "task Done!!!"
    task['finish_time'] = datetime.now()
    if finish_tag in task_log['running_log']:
        task['status'] = "done"
    else:
        task['abort_times'] += 1
        if task['abort_times'] <= task['max_abort_times']:
            task['status'] = "aborted"
        else:
            task['status'] = "aborted %d times." % task['abort_times']

    task.save()


def update_task():
    tasks = GpuTask.objects(status='running').all()
    machines = Machine.objects().all()
    machine_dict = {m['name']: m for m in machines}

    for tasks in tasks:
        try:
            log_request = requests.get("http://%s/containers/%s/logs?stdout=1&stderr=1" % (machine_dict[tasks['running_machine']]['host'], tasks['running_id'][:12]))
            task_log = GpuTaskLog.objects(gpu_mission_name=tasks['name']).first()
            task_log['running_log'] = log_request.text
            task_log.save()
            r = requests.get("http://%s/containers/%s/json" % (machine_dict[tasks['running_machine']]['host'], tasks['running_id'][:12])).json()
            tasks['status'] = r['State']['Status']
            if tasks['status'] != 'running':
                check_result(tasks, task_log)
            tasks['error_log'] = ''
        except Exception as e:
            tasks['error_log'] = str(e)
        tasks['update_time'] = datetime.now()
        tasks.save()


def deploy_task(machine, task):
    # check images
    has_image = check_image_exist(machine, task['docker'])
    if not has_image:
        download_image(machine, task['docker'])
        task['status'] = 'downloading'
        task.save()
        return

    # handle log
    task_log = GpuTaskLog.objects(gpu_task_name=task['name']).first()
    if not task_log:
        task_log = GpuTaskLog(gpu_mission_name=task['name'])
        task_log.save()
    elif task_log['running_log']:
        task_log['pre_logs'] += task_log['running_log'] + '\n' + '-'*50 + '\n'*2
        task_log['running_log'] = ''
        task_log.save()

    # handle tensorboard port
    task['mount_port'], machine['ports'] = machine.ports[0], machine['ports'][1:]

    speech_path = "/ssd/speech"
    output_path = "/ssd/speech_output/{}".format(task['name'])
    task_command = task['command'].strip() + ' -w ' + output_path
    post_data = {
        "Image": task['docker'],
        "Env": ["LD_PRELOAD=/usr/lib/libtcmalloc.so"],
        "Volumes": {
            cuda_lib: {}
            for cuda_lib in machine['cuda_libs']
            },
        "ExposedPorts": {
            "6006/tcp": {}
        },
        "Entrypoint": ["python", "-u", "entry.py",
                       os.environ['GITHUB_USERNAME'], os.environ['GITHUB_PASSWORD'],
                       task['repo'], task['branch'],
                       task_command, task['name']],
        "HostConfig": {
            "Binds": [
                         '%s:%s' % (cuda_lib, cuda_lib)
                         for cuda_lib in machine['cuda_libs']
                         ] + machine['ro_cuda_libs'] +
                     ['%s:%s' % (output_path, output_path)],
            "Devices": [{"PathOnHost": machine['available_gpus'][i],
                         "PathInContainer": "/dev/nvidia%d" % i,
                         "CgroupPermissions": "mrw"}
                        for i in range(task['gpu_num'])] +
                       [{"PathOnHost": dev,
                         "PathInContainer": dev,
                         "CgroupPermissions": "mrw"} for dev in machine['devices']],
            "PortBindings": {"6006/tcp": [{"HostPort": str(task['mount_port'])}]},
        }
    }
    if task['volumes']:
        post_data['HostConfig']['Binds'].extend([v.strip() for v in task['volumes'].split(',')])

    post_data['HostConfig']['Binds'] += ['%s:%s' % (speech_path, speech_path)]

    create_url = 'http://' + machine['host'] + '/containers/create?name=%s' % task['name']
    start_url = 'http://' + machine['host'] + '/containers/{}/start'
    try:
        resp = requests.post(create_url, json=post_data)
        if resp.status_code >= 400:
            if resp.status_code == 409:
                # try to delete exist container
                delete_url = 'http://' + machine['host'] + '/containers/{}'.format(task['name'])
                delete_resp = requests.delete(delete_url)
                if delete_resp.status_code == 204:
                    resp = requests.post(create_url, json=post_data)
                    if resp.status_code >= 400:
                        raise Exception('create failed. code={}. {}'.format(resp.status_code, resp.text))
                    logging.info('deploy gpu task %s on %s' % (task['name'], machine['name']))
                else:
                    raise Exception('delete {} failed. code={}. {}'.format(task['name'], delete_resp.status_code, delete_resp.text))
            else:
                raise Exception('create failed. code={}. {}'.format(resp.status_code, resp.text))
        r = resp.json()
        task['running_id'] = r['Id']
        task['running_machine'] = machine['name']
        task['running_gpu'] = machine['available_gpus'][:task['gpu_num']]
        task['start_time'] = datetime.now()
        task['finish_time'] = None
        resp = requests.post(start_url.format(r['Id'][:12]))
        if resp.status_code >= 400:
            raise Exception('start failed. code={}. {}'.format(resp.status_code, resp.text))
        task['status'] = 'running'
        task['error_log'] = ''
    except Exception as e:
        task['status'] = 'start failed'
        task['error_log'] = str(e)
        logging.error(e)

    task.save()


def deploy(machines):
    for machine in machines:
        rest_gpus = len(machine['available_gpus'])
        if rest_gpus == 0:
            continue
        next_job = GpuTask.objects(running_machine=machine['name'], status='aborted').first()
        if not next_job:
            next_job = GpuTask.objects(machine__contains=machine['name'], status='queueing').first()
        if not next_job:
            continue
        if next_job['gpu_num'] > rest_gpus:
            continue
        if not machine.ports:
            continue
        deploy_task(machine, next_job)


def check_downloading_tasks():
    tasks = GpuTask.objects(status='downloading').all()
    machines = Machine.objects().all()
    machine_dict = {m['name']: m for m in machines}
    for task in tasks:
        if check_image_exist(machine_dict[task['running_machine']], task['docker']):
            task['status'] = 'queueing'
            task.save()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    db.connect(mongo_config['DB'],
               host="%s:%s" % (mongo_config['host'], mongo_config['port']))
    logging.info("gpud start")
    Gpu.drop_collection()
    init_gpu(Machine.objects(accept_jobs__contains='gpu').all())
    while True:
        machines = update_machine()
        update_task()
        check_downloading_tasks()
        deploy(machines)
        time.sleep(SLEEP)
