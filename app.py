# ./app.py

from flask import Flask, render_template, request, jsonify
from pusher import Pusher
import json
import sqlite3
from flask import g

# create flask app
app = Flask(__name__)

# configure pusher object
pusher = Pusher(
  app_id = "734358",
  key = "47bd5e95a97b6c383eee",
  secret = "f4c6e0a9c545b7dcc28a",
  cluster = "us2",
  ssl=True
)


# database connection
DATABASE = './database.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# close database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# index route, shows index.html view
@app.route('/')
def index():
    return render_template('index.html')

# endpoint for storing todo item
@app.route('/add-todo', methods = ['POST'])
def addTodo():
    conn = get_db()
    cur = conn.cursor()

    # load JSON data from request
    data = json.loads(request.data)

    # insert data into database
    columns = ', '.join(data.keys())
    placeholders = ', '.join('?' * len(data))
    sql = 'INSERT into base_tasks ({}) VALUES ({})'.format(columns, placeholders)
    cur.execute(sql, (data['time'], data['task'], data['assignee'], data['overdue'], data['comment'], data['completed']))
    conn.commit()

    # query to get task id
    sql = 'select id from base_tasks where time=="%s" and task=="%s"' % (data['time'], data['task'])
    id = cur.execute(sql)
    data['id'] = id.fetchall()[0]

    # trigger `item-added` event on `todo` channel
    pusher.trigger('todo', 'item-added', data)

    return jsonify(data)

@app.route('/get_all_tasks/')
def get_all_tasks():
    conn = get_db()
    cur = conn.cursor()

    sql = 'select * from base_tasks'
    cur.execute(sql)
    all_tasks = cur.fetchall()
    tasks_list = []
    for task in all_tasks:
        task_dict = {
                    'id': task[0],
                    'time': task[1],
                    'task': task[2],
                    'assignee': task[3],
                    'overdue': task[4],
                    'comment': task[5],
                    'completed': task[6]
                    }
        tasks_list.append(task_dict)


    return jsonify(tasks_list)



# endpoint for deleting todo item
@app.route('/remove-todo/<item_id>')
def removeTodo(item_id):
    conn = get_db()
    cur = conn.cursor()

    data = {'id': item_id }
    pusher.trigger('todo', 'item-removed', data)

    sql = 'delete from base_tasks where id == "%s"' % item_id
    cur.execute(sql)
    conn.commit()

    return jsonify(data)

# endpoint for updating todo item
@app.route('/update-todo/<item_id>', methods = ['POST'])
def updateTodo(item_id):
    data = {
    'id': item_id,
    'completed': json.loads(request.data).get('completed', 0)
    }
    pusher.trigger('todo', 'item-updated', data)
    return jsonify(data)

# run Flask app in debug mode
app.run(debug=True)
