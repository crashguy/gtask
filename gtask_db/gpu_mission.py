from datetime import datetime

from gtask_db import db

machine_list = [
    'octp',
    'octo',
    'quad0',
    'quad1',
    'quad2',
    'quad3',
    'quad4',
    'quad5',
    'quad6',
]


class GpuMission(db.Document):
    name = db.StringField(max_length=128, unique=True)
    docker = db.StringField(max_length=100)
    machine = db.StringField(max_length=40, choices=machine_list)
    volumes = db.StringField(max_length=128)
    gpu_num = db.IntField(default=4)
    repo = db.StringField(max_length=128, default='github.com/naturali/dnn')
    branch = db.StringField(max_length=40, default='master')
    command = db.StringField(max_length=1024)

    git_username = db.StringField(max_length=30)
    git_passwd = db.StringField(max_length=30)

    init_time = db.DateTimeField(default=datetime.now())
    status = db.StringField(max_length=20, default="queueing")

    running_machine = db.StringField(max_length=128)
    running_gpu = db.ListField(db.StringField())
    running_id = db.StringField(max_length=70)
    running_pid = db.StringField(max_length=30)
    error_log = db.StringField(default='')
    arrange_time = db.DateTimeField()
    start_time = db.DateTimeField()
    finish_time = db.DateTimeField()
    update_time = db.DateTimeField()

    abort_times = db.IntField(default=0)
    max_abort_times = db.IntField(default=3)

    mount_port = db.IntField()


class GpuMissionLog(db.Document):
    # name = db.StringField()
    gpu_mission_name = db.StringField(max_length=128)
    pre_logs = db.StringField(default='')
    running_log = db.StringField(default='')
