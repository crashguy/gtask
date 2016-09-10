from datetime import datetime, timedelta

from flask import Markup
from flask_admin.contrib.mongoengine import ModelView

from gtask_db.mission import Machine


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

class MissionView(ModelView):
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
    column_list = ['name', 'container_num', 'cpu', 'memory', 'last_update']
    form_columns = ['name', 'host', 'plugin']
    column_formatters = dict(
        last_update=datetime_formatter,
        name=machine_name_formatter,
        container_num=contain_list_formatter
    )
