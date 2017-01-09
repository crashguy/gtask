from gtask_db import db
from env import mongo_config
from gtask_db.gpu_mission import GpuTask, GpuMissionLog


def main():
    db.connect(mongo_config['DB'],
               host="%s:%s" % (mongo_config['host'], mongo_config['port']))

    missions = GpuTask.objects().all()
    for mission in missions:
        mission_log = GpuMissionLog.objects(gpu_mission_name=mission['name']).first()
        if not mission_log:
            mission_log = GpuMissionLog(gpu_mission_name=mission['name'])
            mission_log.save()
            print('create %s log' % mission['name'])
        # mission_log['pre_logs'] = mission['pre_logs']
        # mission_log['running_log'] = mission['running_log']
        # mission['pre_logs'] = ''
        # mission['running_log'] = ''
        # mission_log.save()
        # mission.save()


if __name__ == '__main__':
    main()