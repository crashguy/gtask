from datetime import datetime

from gtask_db import db


class Mission(db.Document):
    job = db.StringField(max_length=128)
    name = db.StringField(max_length=128)
    docker = db.StringField(max_length=40)
    machine = db.StringField(max_length=40)
    volumes = db.StringField(max_length=128)
    gpu_num = db.IntField()
    repo = db.StringField(max_length=128)
    branch = db.StringField(max_length=40)
    command = db.StringField(max_length=256)

    init_time = db.DateTimeField(default=datetime.now())
    status = db.StringField(max_length=20)

    running_machine = db.StringField(max_length=128)
    running_gpu = db.StringField(max_length=128)
    running_id = db.StringField(max_length=70)
    arrange_time = db.DateTimeField()
    start_time = db.DateTimeField()
    finish_time = db.DateTimeField()


class GpuMission(db.Document):
    name = db.StringField(max_length=128)
    machine = db.StringField(max_length=40)
    volumes = db.StringField(max_length=128)
    gpu_num = db.IntField()
    repo = db.StringField(max_length=128)
    branch = db.StringField(max_length=40)
    command = db.StringField(max_length=256)

    init_time = db.DateTimeField(default=datetime.now())
    status = db.StringField(max_length=20)

    running_machine = db.StringField(max_length=128)
    running_gpu = db.StringField(max_length=128)
    running_id = db.StringField(max_length=70)
    arrange_time = db.DateTimeField()
    start_time = db.DateTimeField()
    finish_time = db.DateTimeField()


class Machine(db.Document):
    name = db.StringField(max_length=40)
    host = db.StringField(max_length=20)
    plugin = db.StringField(max_length=20)
    cuda_libs = db.ListField(db.StringField())
    ro_cuda_libs = db.ListField(db.StringField())

    cpu = db.StringField(max_length=20)
    memory = db.StringField(max_length=40)
    gpu = db.DictField()
    container_num = db.IntField()
    containers = db.StringField()
    last_update = db.DateTimeField()
    gpu_last_update = db.DateTimeField()


class Gpu(db.Document):
    order = db.IntField()
    path = db.StringField(max_length=20)
    model = db.StringField(max_length=30)
    machine = db.ReferenceField("Machine")
    power = db.IntField()
    max_power = db.IntField()
    temperature = db.IntField()
    processes = db.StringField(max_length=30)




