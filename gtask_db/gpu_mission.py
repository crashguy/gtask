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
    command = db.StringField(max_length=256)

    git_username = db.StringField(max_length=30)
    git_passwd = db.StringField(max_length=30)

    init_time = db.DateTimeField(default=datetime.now())
    status = db.StringField(max_length=20, default="queueing")

    running_machine = db.StringField(max_length=128)
    running_gpu = db.ListField(db.StringField())
    running_id = db.StringField(max_length=70)
    running_pid = db.StringField(max_length=30)
    error_log = db.StringField()

    arrange_time = db.DateTimeField()
    start_time = db.DateTimeField()
    finish_time = db.DateTimeField()
