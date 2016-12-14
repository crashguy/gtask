from datetime import datetime

from gtask_db import db


class GpuMission(db.Document):
    name = db.StringField(max_length=128)
    docker = db.StringField(max_length=100)
    machine = db.StringField(max_length=40)
    volumes = db.StringField(max_length=128)
    gpu_num = db.IntField()
    repo = db.StringField(max_length=128)
    branch = db.StringField(max_length=40)
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
    pre_logs = db.StringField(default='')
    running_log = db.StringField()

    arrange_time = db.DateTimeField()
    start_time = db.DateTimeField()
    finish_time = db.DateTimeField()
    update_time = db.DateTimeField()

    abort_times = db.IntField(default=0)
    max_abort_times = db.IntField(default=10)


class GpuMissionConfig(db.Document):
    # name = db.StringField()
    gpu_mission_name = db.StringField(max_length=128)
    config_file_path = db.StringField(default="speech/config.py")
    content = db.StringField()
    disk_path = db.StringField()

