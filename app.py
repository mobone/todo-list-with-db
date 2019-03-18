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
                    'comment': task[5]
                    }
        tasks_list.append(task_dict)


    return jsonify(tasks_list)

# endpoint for deleting todo item
@app.route('/remove-todo/<item_id>')
def removeTodo(item_id):
    conn = get_db()
    cur = conn.cursor()

    data = {'id': item_id }

    sql = 'delete from base_tasks where id == "%s"' % item_id
    cur.execute(sql)
    conn.commit()

    return jsonify(data)

# endpoint for adding a user and rending main page
@app.route('/add-users', methods = ['GET','POST'])
def add_users_page():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        sql = 'select * from users where firstname=="%s" and lastname=="%s"' % (request.form['firstName'], request.form['lastName'])
        cur.execute(sql)
        matched_users = cur.fetchall()
        if len(matched_users):
            print('user already exists')
        else:            
            sql = 'INSERT into users (firstname, lastname, usertype) VALUES (?,?,?)'
            cur.execute(sql, (request.form['firstName'],request.form['lastName'],request.form['userType']))
            conn.commit()
            print('user added')
    return render_template('add_users.html')

@app.route('/get_all_users')
def get_all_users():
    conn = get_db()
    cur = conn.cursor()
    sql = 'select * from users'
    cur.execute(sql)
    all_users = cur.fetchall()
    users_list = []
    for user in all_users:
        user_dict = {
                    'firstname': user[0],
                    'lastname': user[1],
                    'usertype': user[2]
                    }
        users_list.append(user_dict)
    print('returning users', users_list)
    return jsonify(users_list)

@app.route('/remove-user', methods = ['POST'])
def remove_user():
    conn = get_db()
    cur = conn.cursor()
    sql = 'delete from users where firstname == "%s" and lastname == "%s"' % (request.form['firstname'], request.form['lastname'])
    cur.execute(sql)
    conn.commit()
    return render_template('add_users.html')


# run Flask app in debug mode
app.run(debug=True)
