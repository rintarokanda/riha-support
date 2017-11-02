from __future__ import print_function
from flask.ext.script import Manager
from flaskr import app, db
print(app.url_map)
app.run(host='0.0.0.0', port=5000, debug=True)

manager = Manager(app)

@manager.command
def init_db():
    db.create_all()

if __name__ == '__main__':
    manager.run()
