import logging
import time
from datetime import datetime

import requests

from env import mongo_config
from gtask_db.mission import Mission, Machine, db

SLEEP = 15
MISSION_LIMIT = 40


def update_machine():
    machines = Machine.objects().all()
    for m in machines:
        try:
            r = requests.get("http://%s/info" % m['host']).json()
            m['container_num'] = r['ContainersRunning']
            m['last_update'] = datetime.now()
            m.save()
        except Exception as e:
            logging.error(e.message)
    return machines


def update_mission():
    pass


def deploy_mission(machine, mission):
    post_data = {
        "Image": mission['docker'],
        "Volumes": dict({'/home/t430': {}, '/zfs': {}, '/data':{} }),
        "Entrypoint": mission['command'].split(),
        "HostConfig": {
            "Binds": ['/home/t430:/home/t430', '/zfs:/zfs', '/data:/data'],
            "Devices": []
        }
    }
    create_url = 'http://' + machine['host'] + '/containers/create?name=%s' % mission['name']
    start_url = 'http://' + machine['host'] + '/containers/{}/start'
    try:
        r = requests.post(create_url, json=post_data).json()
        mission['running_id'] = r['Id']
        r = requests.post(start_url.format(r['Id'][:12]))
        if r.status_code >= 400:
            raise Exception('start failed. code={}. {}'.format(r.status_code, r.text))
        mission['status'] = 'started'
    except Exception as e:
        mission['status'] = 'start failed'
        logging.error(e.message)

    mission.save()


def deploy(machines):
    for machine in machines:
        post_num = MISSION_LIMIT - machine['container_num']
        if post_num > 0:
            missions = Mission.objects(machine=machine['name'], status='queueing').limit(post_num)
            for mission in missions:
                deploy_mission(machine, mission)

if __name__ == '__main__':
    db.connect(mongo_config['DB'],
               host="%s:%s" % (mongo_config['host'], mongo_config['port']))
    while True:
        machines = update_machine()
        update_mission()
        deploy(machines)
        time.sleep(15)
