# ./app.py


from flask import Flask, flash, redirect, render_template, request, session, abort, g, jsonify, url_for
import json
import sqlite3
import os
from datetime import datetime
from flask_socketio import SocketIO
from datetime import datetime, timedelta
from flask_login import current_user, login_user
from app.models import User
from app import app
from app.forms import LoginForm
from flask_login import logout_user
from flask_login import login_required

socketio = SocketIO(app)
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
"""
# index route, shows index.html view
@app.route('/')
def home():
    return render_template('index.html')
"""
@app.route('/base_tasks')
@login_required
def base_tasks():
    #print("got session useranem", session['username'])
    return render_template('base_tasks.html')

# endpoint for storing todo item
@app.route('/add-todo', methods = ['POST'])
@login_required
def addTodo():
    conn = get_db()
    cur = conn.cursor()

    # load JSON data from request
    data = json.loads(request.data)

    # insert data into database
    columns = ', '.join(data.keys())
    placeholders = ', '.join('?' * len(data))
    sql = 'INSERT into base_tasks ({}) VALUES ({})'.format(columns, placeholders)
    cur.execute(sql, (data['time'], data['shift'], data['task'], data['assignee'], data['overdue'], data['comment'], data['completed']))
    conn.commit()

    # query to get task id
    sql = 'select id from base_tasks where time=="%s" and task=="%s"' % (data['time'], data['task'])
    id = cur.execute(sql)
    data['id'] = id.fetchone()[0]


    return jsonify(data)

@app.route('/get_all_tasks')
@login_required
def get_all_tasks():

    conn = get_db()
    cur = conn.cursor()

    sql = 'select * from base_tasks'
    cur.execute(sql)
    all_tasks = cur.fetchall()
    print(all_tasks)
    tasks_list = []
    for task in all_tasks:

        task = list(task)
        if '.' in task[1]:
            task[1] = task[1].split('.')[0]
        if task[6] is not None and '.' in task[6]:
            task[6] = task[6].split('.')[0]

        for i in range(len(task)):
            if task[i] is None:
                task[i] = ""

        task_dict = {
                    'id': task[0],
                    'time': task[1],
                    'shift': task[2],
                    'task': task[3],
                    'completed': task[4],
                    'assignee': task[5],
                    'overdue': task[6],
                    'comment': task[7]
                    }
        tasks_list.append(task_dict)


    return jsonify(tasks_list)

# endpoint for deleting todo item
@app.route('/remove-todo/<item_id>')
@login_required
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
@login_required
def add_users_page():
    print('got request', request.form)
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        sql = 'select * from user where username=="%s"' % (request.form['username'])
        cur.execute(sql)
        matched_users = cur.fetchall()
        if request.form['userid'] != "":
            print('updating user')
            sql = 'update user set firstname = "%s", lastname = "%s", username = "%s", password_hash = "%s", usertype = "%s" where id == %s' % (request.form['firstName'],request.form['lastName'], request.form['username'], request.form['password'], request.form['userType'], request.form['userid'])
            cur.execute(sql)
            conn.commit()
        elif len(matched_users):
            print('user already exists')
        else:
            sql = 'INSERT into user (firstname, lastname, username, password_hash, usertype) VALUES (?,?,?,?,?)'
            cur.execute(sql, (request.form['firstName'],request.form['lastName'], request.form['username'], request.form['password'], request.form['userType']))
            conn.commit()
            print('user added')
    return render_template('add_users.html')

@app.route('/get_all_users')
@login_required
def get_all_users():
    conn = get_db()
    cur = conn.cursor()
    sql = 'select * from user'
    cur.execute(sql)
    all_users = cur.fetchall()
    users_list = []
    for user in all_users:
        user_dict = {
                    'id': user[0],
                    'username': user[1],
                    'firstname': user[2],
                    'lastname': user[3],

                    'userType': user[5]
                    }
        users_list.append(user_dict)

    return jsonify(users_list)

@app.route('/remove-user', methods = ['POST'])
@login_required
def remove_user():
    conn = get_db()
    cur = conn.cursor()
    sql = 'delete from user where username=="%s"' % (request.form['username'])
    cur.execute(sql)
    conn.commit()
    return render_template('add_users.html')

@app.route('/copy-to-today', methods = ['POST'])
@login_required
def copy_tasks_to_today():
    date = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cur = conn.cursor()
    sql = 'select * from base_tasks'
    cur.execute(sql)
    tasks = cur.fetchall()


    for task in tasks:
        task = list(task)
        if '.' in task[1]:
            task[1] = task[1].split('.')[0]
        if task[6] is not None and '.' in task[6]:
            task[6] = task[6].split('.')[0]
        for i in range(len(task)):
            if task[i] is None:
                task[i] = ""
        day_comment = task[7]

        todays_day = datetime.today().strftime('%A')

        if day_comment == '':
            add_row_to_today(date, task)
        elif todays_day.lower() in day_comment.lower() and 'Not '.lower()+todays_day.lower() not in day_comment.lower():
            add_row_to_today(date, task)



    conn.commit()

    return render_template('user_page.html')

def add_row_to_today(date,task):
    conn = get_db()
    cur = conn.cursor()
    sql = 'INSERT into todays_tasks ("date","time","shift","task","completed","assignee","overdue","comments") VALUES (?,?,?,?,?,?,?,?)'
    cur.execute(sql, (date,task[1],task[2],task[3],task[4],task[5],task[6],""))
    conn.commit()


@app.route('/')
@app.route('/index')
@app.route('/user-page')
@login_required
def index():

    return render_template('user_page.html')

@app.route('/get-todays-tasks')
@login_required
def todays_tasks():
    #print('here', session['username'])
    conn = get_db()
    cur = conn.cursor()
    sql = 'select * from todays_tasks where date=="%s" or date=="%s"' % (datetime.now().strftime("%Y-%m-%d"), (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))
    cur.execute(sql)
    all_tasks_db = cur.fetchall()
    all_tasks_dict = {}
    todays_tasks_list = []
    for task in all_tasks_db:
        task_dict = {
                    'id': task[0],
                    'date': task[1],
                    'time': task[2],
                    'shift': task[3],
                    'task': task[4],
                    'completed': task[5],
                    'assignee': task[6],
                    'overdue': task[7],
                    'comment': task[8],

                    }
        todays_tasks_list.append(task_dict)

    #sql = 'select * from todays_tasks where date=="%s" and assignee=="%s"' % (datetime.now().strftime("%Y-%m-%d"), session.get('username'))

    username = current_user.get_username()
    sql = 'select * from todays_tasks where date=="%s" and assignee=="%s"' % (datetime.now().strftime("%Y-%m-%d"), username)
    cur.execute(sql)
    my_tasks_db = cur.fetchall()
    my_tasks_list = []
    for task in my_tasks_db:
        task_dict = {
                    'id': task[0],
                    'date': task[1],
                    'time': task[2],
                    'shift': task[3],
                    'task': task[4],
                    'completed': task[5],
                    'assignee': task[6],
                    'overdue': task[7],
                    'comment': task[8]
                    }
        my_tasks_list.append(task_dict)

    all_tasks_dict['todays_tasks'] = todays_tasks_list
    all_tasks_dict['my_tasks'] = my_tasks_list

    return jsonify(all_tasks_dict)

@app.route('/assign-item', methods=['POST'])
@login_required
def assign_item():
    data = json.loads(request.data)

    item_id = data['item_id']
    conn = get_db()
    cur = conn.cursor()
    print('>>>>>>>>>>>>', session.get(''))
    #sql = 'update todays_tasks set assignee = "%s" where id=="%s"' % (session.get('username'), item_id)
    username = current_user.get_username()
    sql = 'update todays_tasks set assignee = "%s" where id=="%s"' % (username, item_id)
    cur.execute(sql)
    conn.commit()
    sql = 'select * from todays_tasks where id=="%s"' % (item_id)
    cur.execute(sql)
    row = cur.fetchone()
    print(row)
    task_dict = {
                'id': row[0],
                'date': row[1],
                'time': row[2],
                'shift': row[3],
                'task': row[4],
                'completed': row[5],
                'assignee': row[6],
                'overdue': row[7],
                'comment': row[8]

                }
    socketio.emit('assign', {'id': item_id, 'assignee': task_dict['assignee']})
    return jsonify(task_dict)

@app.route('/unassign-item/<item_id>')
@login_required
def unassign_item(item_id):
    print('unassigning', item_id)
    conn = get_db()
    cur = conn.cursor()
    sql = 'update todays_tasks set assignee= "%s" where id == "%s"' % ("",item_id)
    cur.execute(sql)
    conn.commit()
    data = {'id': item_id}
    socketio.emit('unassign', {'id': item_id})
    return jsonify(data)


@app.route('/complete-item/<item_id>/<shift>/')
@login_required
@socketio.on('completed')
def complete_item(item_id, shift):
    print("completing", item_id)
    conn = get_db()
    cur = conn.cursor()
    sql = 'update todays_tasks set completed = "%s" where id == "%s"' % (1,item_id)
    cur.execute(sql)
    conn.commit()
    data = {'id': item_id}
    socketio.emit('completed', {'id': item_id, 'shift': shift})
    return jsonify(data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

from flask import send_from_directory

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
