import os
import sys

self_dir = os.path.abspath(os.path.join(__file__, os.pardir)) + '/'
work_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)) + '/'
if work_dir not in sys.path:
    sys.path.insert(0, work_dir)

from env import DEBUG, PORT
from gtask_admin.app import gtask_admin, app, mongo_config
from gtask_admin.views.views import CpuMissionView, MachineView, \
    GpuTaskView, GpuView
from gtask_db import db
from gtask_db.machine import Machine, Gpu
from gtask_db.cpu_mission import Mission
from gtask_db.gpu_mission import GpuMission

db.connect(mongo_config['DB'],
           host="%s:%s" % (mongo_config['host'], mongo_config['port']))
# Add views
# db.init_app(app)
# gtask_admin.add_view(CpuMissionView(Mission))
gtask_admin.add_view(GpuTaskView(GpuMission))
gtask_admin.add_view(MachineView(Machine))
gtask_admin.add_view(GpuView(Gpu))

application = app

# Start app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG, port=PORT)
