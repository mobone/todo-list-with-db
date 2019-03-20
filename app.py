# ./app.py


from flask import Flask, flash, redirect, render_template, request, session, abort, g, jsonify, url_for
import json
import sqlite3
import os
from datetime import datetime
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
def home():
    return render_template('index.html')

@app.route('/base_tasks')
def base_tasks():
    return render_template('base_tasks.html')

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

@app.route('/get_all_tasks')
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
        sql = 'select * from users where username=="%s"' % (request.form['username'])
        cur.execute(sql)
        matched_users = cur.fetchall()
        if len(matched_users):
            print('user already exists')
        else:
            sql = 'INSERT into users (firstname, lastname, username, password, usertype) VALUES (?,?,?,?,?)'
            cur.execute(sql, (request.form['firstName'],request.form['lastName'], request.form['username'], request.form['password'], request.form['userType']))
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
                    'username': user[2],
                    'password': user[3],
                    'userType': user[4]
                    }
        users_list.append(user_dict)
    print('returning users', users_list)
    return jsonify(users_list)

@app.route('/remove-user', methods = ['POST'])
def remove_user():
    conn = get_db()
    cur = conn.cursor()
    sql = 'delete from users where username=="%s"' % (request.form['username'])
    cur.execute(sql)
    conn.commit()
    return render_template('add_users.html')

@app.route('/copy-to-today', methods = ['POST'])
def copy_tasks_to_today():
    date = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cur = conn.cursor()
    sql = 'select * from base_tasks'
    cur.execute(sql)
    tasks = cur.fetchall()
    for task in tasks:

        sql = 'INSERT into todays_tasks ("date","time","task","assignee","overdue","comment","completed") VALUES (?,?,?,?,?,?,?)'
        cur.execute(sql, (date,task[0],task[1],task[2],task[3],task[4],task[5]))
    conn.commit()

    return render_template('user_page.html')

@app.route('/user-page')
def user_page():
    return render_template('user_page.html')

@app.route('/get-todays-tasks')
def todays_tasks():
    conn = get_db()
    cur = conn.cursor()
    sql = 'select * from todays_tasks where date=="%s"' % (datetime.now().strftime("%Y-%m-%d"))

    cur.execute(sql)
    all_tasks = cur.fetchall()
    tasks_list = []
    for task in all_tasks:
        task_dict = {
                    'time': task[1],
                    'task': task[2],
                    'assignee': task[3],
                    'overdue': task[4],
                    'comment': task[5]
                    }
        tasks_list.append(task_dict)


    return jsonify(tasks_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        sql = 'select username,password from users where username == "%s"' % request.form['username']
        cur.execute(sql)
        user_values = cur.fetchone()

        if user_values is None:
            error = 'Invalid credentials'
            return render_template('index.html', error=error)
        user = {'username': user_values[0],
                'password': user_values[1]}
        if request.form['username'] != user['username'] or \
                request.form['password'] != user['password']:
            error = 'Invalid credentials'
        else:
            session['logged_in'] = True
            return redirect(url_for('base_tasks'))
    return render_template('index.html', error=error)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

if __name__ == "__main__":
    # run Flask app in debug mode
    app.secret_key = os.urandom(12)
    app.run(debug=True)
    #app.run(debug=True,host='0.0.0.0', port=4000)
