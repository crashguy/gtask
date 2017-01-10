# encoding: utf-8

from datetime import datetime, timedelta

from flask import Markup, url_for
from flask_admin import expose
from flask_admin.base import AdminIndexView
from flask_admin.contrib.mongoengine import ModelView
from wtforms.fields import StringField, TextAreaField
from wtforms.widgets import TextInput, HTMLString
from collections import defaultdict

from gtask_db.gpu_mission import GpuTask
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


def task_name_formatter(view, context, model, name):
    url = '/admin/gputask/edit?id=%s' % model['id']
    return Markup("<a href={}>{}</a>".format(url, model[name]))


def pid_formatter(view, context, model, name):
    pids = model[name]
    if not pids:
        return ''
    else:
        pids = pids.split(',')
    mission = GpuTask.objects(running_pid__in=pids).first()
    if mission:
        return '%s(%s)' % (model[name], mission['name'])
    else:
        return '%s' % model[name]


def running_log_formatter(view, context, model, name):
    return Markup('<a href="/gpu_task/{task_name}/log/">view log</a>'.format(
        task_name=model['name']
    ))


def status_formatter(view, context, model, name):
    if model['status'] == 'running':
        return Markup('<a href="#" class="stop_mission" mission="{task_name}" machine="{machine_name}">running</a>'.format(
            task_name=model['name'],
            machine_name=model['running_machine']
        ))
    return model['status']


def tensorboard_formatter(view, context, model, name):
    if model['status'] == 'running' and model['mount_port']:
        machine = Machine.objects(name=model['running_machine']).first()
        ip = machine['host'].split(":")[0]
        return Markup('<a href="http://%s:%s">link</a>'% (ip, model['mount_port']))
    return ''


def status_key(mission):
    x = mission['status']
    status_mapping = defaultdict(lambda: 10)
    status_mapping['running'] = 1
    status_mapping['start_failed'] = 2
    status_mapping['finish'] = 3
    status_mapping['aborted'] = 4
    status_mapping['manual_abort'] = 5
    status_mapping['manual_aborted'] = 5
    return status_mapping[x], x


class MissionNameInputs(TextInput):
    def __call__(self, field, **kwargs):
        button_html = '&nbsp;&nbsp;&nbsp; <input type="button" id="load_config" value="load_config"/>'
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return HTMLString('<input %s>' % self.html_params(name=field.name, **kwargs) + button_html)


class MissionNameFields(StringField):
    widget = MissionNameInputs()


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
    column_default_sort = ('name', False)


class GpuTaskView(ModelView):
    column_list = ['name', 'status', 'running_machine', 'running_gpu',
                   'start_time', 'finish_time', 'error_log', 'running_log', 'tensorboard']
    form_columns = ['name', 'max_abort_times', 'status', 'docker', 'machine', 'volumes', 'gpu_num', 'repo',
                    'branch', 'command']
    column_filters = ['status', ]
    column_formatters = dict(
        start_time=datetime_formatter,
        finish_time=datetime_formatter,
        update_time=datetime_formatter,
        running_log=running_log_formatter,
        status=status_formatter,
        tensorboard=tensorboard_formatter,
        name=task_name_formatter
    )

    form_overrides = dict(
        # name=MissionNameFields,
        command=TextAreaField
    )
    create_template = "models/gpu_mission_edit.html"
    edit_template = "models/gpu_mission_edit.html"
    list_template = "models/gpu_mission_list.html"
    column_default_sort = ('start_time', True)

    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True, page_size=None):
        count, query = super(GpuTaskView, self).get_list(
            page, sort_column, sort_desc, search, filters, execute, page_size
        )
        if not sort_column:
            new_query = sorted(query, key=status_key)
            return count, new_query
        return count, query


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
        processes=pid_formatter
    )


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('home.html')
