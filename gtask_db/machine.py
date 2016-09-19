from gtask_db import db


class Machine(db.Document):
    accept_jobs = db.StringField(max_length=40, default="")
    name = db.StringField(max_length=40)
    host = db.StringField(max_length=20)
    plugin = db.StringField(max_length=20)

    cuda_libs = db.ListField(db.StringField(), default=[])
    ro_cuda_libs = db.ListField(db.StringField(), default=[])
    devices = db.ListField(db.StringField())

    cpu = db.StringField(max_length=20)
    memory = db.StringField(max_length=40)
    gpu = db.DictField()
    available_gpus = db.ListField(db.StringField())


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

    init_time = db.DateTimeField()
    last_update = db.DateTimeField()
