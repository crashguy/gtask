from env import DEBUG, PORT
from gtask_admin.app import gtask_admin, app, mongo_config
from gtask_admin.views.views import MissionView, MachineView
from gtask_db.mission import Mission, Machine, db

db.connect(mongo_config['DB'],
           host="%s:%s" % (mongo_config['host'], mongo_config['port']))
# Add views
# db.init_app(app)
gtask_admin.add_view(MissionView(Mission))
gtask_admin.add_view(MachineView(Machine))

application = app

# Start app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG, port=PORT)
