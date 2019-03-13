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

    data = json.loads(request.data) # load JSON data from request
    pusher.trigger('todo', 'item-added', data) # trigger `item-added` event on `todo` channel


    sql = "insert into base_todo_items_test values (?,?,?)"
    print(data)

    columns = ', '.join(data.keys())
    placeholders = ', '.join('?' * len(data))
    print(columns)
    print(placeholders)
    sql = 'INSERT into todo_list ({}) VALUES ({})'.format(columns, placeholders)
    print(sql)
    print(data.values())

    cur.execute(sql, (data['id'], data['value'], data['completed']))


    conn.commit()
    return jsonify(data)

@app.route('/get_all_tasks/')
def get_all_tasks():
    conn = get_db()
    cur = conn.cursor()

    sql = 'select * from todo_list'
    cur.execute(sql)
    all_tasks = cur.fetchall()
    print('mooo',jsonify(all_tasks))
    return jsonify(all_tasks)



# endpoint for deleting todo item
@app.route('/remove-todo/<item_id>')
def removeTodo(item_id):
    data = {'id': item_id }
    pusher.trigger('todo', 'item-removed', data)
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
