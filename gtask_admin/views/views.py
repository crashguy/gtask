from flask_admin.contrib.mongoengine import ModelView


class MissionView(ModelView):
    column_list = ['name', 'job', 'status', 'running_machine', 'start_time']
    form_columns = ['job', 'name', 'docker', 'machine', 'volumes', 'command', 'status']

    pass


class MachineView(ModelView):
    pass
