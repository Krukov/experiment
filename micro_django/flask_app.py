# -*- coding: utf-8 -*-

import os
import uuid
from sqlite3 import dbapi2 as sqlite3

from flask import Flask, request, g, abort, jsonify, session


app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'tasks.db'),
    SECRET_KEY=os.environ.get('SECRET_KEY', 'SECRET_KEY'),
    DEBUG=True,
))
app.config.from_envvar('FLASK_SETTINGS', silent=True)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = connect_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.before_request
def before_request():
    session.setdefault('id', str(uuid.uuid4()))
    g.db = connect_db()


@app.teardown_appcontext
def teardown_appcontext(error):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/tasks', methods=['GET'])
def _all():
    cur = g.db.execute('SELECT * FROM task WHERE task.session_id=$1 order by id desc',
                       [session.get('id'), ])
    tasks = cur.fetchall()
    return jsonify(**{str(task['id']): {'body': task['body'], 'title': task['title'], 'active': task['is_active']}
                      for task in tasks})


@app.route('/tasks/add', methods=['POST'])
def add():
    data = request.form
    g.db.execute('INSERT INTO task (title, body, session_id, is_active) VALUES ($1, $2, $3, 1)',
                 [data.get('title'), data.get('body'), session.get('id')])
    g.db.commit()
    return jsonify(success='ok')


@app.route('/tasks/<id>', methods=['GET'])
def detail(id):
    task = g.db.execute('SELECT * from task WHERE session_id=$1 AND id=$2 LIMIT 1', [session.get('id'), id]).fetchall()

    if task:
        task = task.pop()
        return jsonify(**{'body': task['body'], 'title': task['title'], 'active': task['is_active']})
    abort(404)


if __name__ == '__main__':
    app.run()
