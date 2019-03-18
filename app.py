# ./app.py

from flask import Flask, render_template, request, jsonify
import json
import sqlite3
from flask import g

# create flask app
app = Flask(__name__)

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
    data['id'] = id.fetchone()[0]

    print(data)
    return jsonify(data)

# run Flask app in debug mode
app.run(debug=True)
