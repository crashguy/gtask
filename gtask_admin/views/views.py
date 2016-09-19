from datetime import datetime, timedelta

from flask import Markup
from flask_admin.contrib.mongoengine import ModelView

from gtask_db.gpu_mission import GpuMission
from gtask_db.machine import Machine


def datetime_formatter(view, context, model, name):
    if not model[name]:
        return ''
    delta_time = datetime.now() - model[name]
    if delta_time < timedelta(minutes=2):
        return '%d seconds ago' % delta_time.seconds
    if delta_time < timedelta(hours=2):
        return '%d minutes ago' % (delta_time.seconds / 60)
    if delta_time < timedelta(days=2):
        return '%d hours ago' % (delta_time.seconds / 60 / 60)
    return '%d days ago' % delta_time.days


def mission_name_formatter(view, context, model, name):
    if model['status'] == 'started':
        machine = Machine.objects(name=model['machine']).first()
        url = 'http://%s/containers/%s/json' % (machine['host'], model['running_id'][:12])
        return Markup("<a href={}>{}</a>".format(url, model['name']))
    else:
        return model['name']


def machine_name_formatter(view, context, model, name):
    url = 'http://%s/info' % (model['host'])
    return Markup("<a href={}>{}</a>".format(url, model['name']))


def contain_list_formatter(view, context, model, name):
    url = 'http://%s/containers/json?all=1' % (model['host'])
    return Markup("<a href={}>{}</a>".format(url, model[name]))


def show_machine_name_formatter(view, context, model, name):
    return model[name]['name']


def pid_formatter_formatter(view, context, model, name):
    pids = model[name]
    if not pids:
        return ''
    else:
        pids = pids.split(',')
    mission = GpuMission.objects(running_pid__in=pids).first()
    if mission:
        return '%s(%s)' % (model[name], mission['name'])
    else:
        return '%s' % model[name]


class CpuMissionView(ModelView):
    column_list = ['name', 'job', 'status', 'running_machine', 'start_time', 'finish_time']
    form_columns = ['job', 'name', 'docker', 'machine', 'volumes', 'command', 'status']
    column_filters = ['name', 'job', 'status', 'running_machine', 'start_time', 'finish_time']
    column_formatters = dict(
        name=mission_name_formatter,
        start_time=datetime_formatter,
        finish_time=datetime_formatter
    )
    pass


class MachineView(ModelView):
    column_list = ['name', 'accept_jobs', 'container_num', 'cpu', 'memory',
                   'available_gpus', 'last_update', 'gpu_last_update']
    form_columns = ['name', 'accept_jobs', 'host', 'plugin', 'cuda_libs', 'ro_cuda_libs', 'devices']
    column_formatters = dict(
        last_update=datetime_formatter,
        gpu_last_update=datetime_formatter,
        name=machine_name_formatter,
        container_num=contain_list_formatter
    )


class GpuMissionView(ModelView):
    column_list = ['name', 'status', 'machine', 'running_machine', 'running_gpu',
                   'running_id', 'running_pid', 'arrange_time', 'start_time',
                   'finish_time', 'error_log']
    form_columns = ['name', 'status', 'docker', 'machine', 'volumes', 'gpu_num', 'repo',
                    'branch', 'command', 'git_username', 'git_passwd']
    column_formatters = dict(
        start_time=datetime_formatter,
        finish_time=datetime_formatter
    )


class GpuView(ModelView):
    can_edit = False
    can_create = False
    can_delete = False
    column_list = ['machine', 'order', 'processes', 'path', 'model', 'power',
                   'max_power', 'temperature', 'init_time', 'last_update']
    column_formatters = dict(
        init_time=datetime_formatter,
        last_update=datetime_formatter,
        machine=show_machine_name_formatter,
        processes=pid_formatter_formatter
    )
