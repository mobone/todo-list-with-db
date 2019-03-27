# ./app.py


from flask import Flask, flash, redirect, render_template, request, session, abort, g, jsonify, url_for
import json
import sqlite3
import os
from datetime import datetime
from flask_socketio import SocketIO
from datetime import datetime, timedelta
from flask_login import current_user, login_user
from app.models import User, Base_Task, Todays_Task
from app import app
from app.forms import LoginForm
from flask_login import logout_user
from flask_login import login_required
from app import db
from sqlalchemy.exc import SQLAlchemyError


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

@app.route('/base_tasks')
@login_required
def base_tasks():
    #print("got session useranem", session['username'])
    return render_template('base_tasks.html')

# endpoint for storing todo item
@app.route('/add-todo', methods = ['POST'])
@login_required
def addTodo(): ## TODO:
    data = json.loads(request.data)

    task = Base_Task(time=data['time'], shift=data['shift'],task=data['task'],overdue=data['overdue'],comments=data['comment'])
    db.session.add(task)
    db.session.commit()

    return jsonify(data)

@app.route('/get_all_tasks')
@login_required
def get_all_tasks():

    base_tasks = Base_Task.query.all()
    tasks_list = []
    for task in base_tasks:
        if task.comments == None:
            task.comments = ''
        task.time = task.time.split('.')[0]
        if task.overdue is not None:
            task.overdue = task.overdue.split('.')[0]
        task_dict = {
                    'id': task.id,
                    'time': task.time,
                    'shift': task.shift,
                    'task': task.task,
                    'overdue': task.overdue,
                    'comment': task.comments
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
    #print('got request', request.form)
    if request.method == 'POST':
        if request.form['userid'] != "":
            user = User.query.filter_by(id=request.form['userid']).first()
            if 'change_password' in request.form.keys() and request.form['change_password'] == 'y':
                user.set_password(request.form['password'])
                db.session.commit()
            else:
                user = User.query.filter_by(id=request.form['userid']).first()
                if len(User.query.filter_by(username=request.form['username']).all()):
                    print('Username already exists')
                else:
                    user.username = request.form['username']
                user.firstname = request.form['firstName']
                user.lastname = request.form['lastName']
                user.usertype = request.form['userType']
                db.session.commit()
        else:
            u = User(username=request.form['username'],firstname=request.form['firstName'],lastname=request.form['lastName'],usertype=request.form['userType'])
            db.session.add(u)
            u.set_password(request.form['password'])
            db.session.commit()
    return render_template('add_users.html')

@app.route('/get_all_users')
@login_required
def get_all_users():
    users = User.query.all()
    users_list = []
    for u in users:
        user_dict = {
                    'id': u.id,
                    'username': u.username,
                    'firstname': u.firstname,
                    'lastname': u.lastname,
                    'userType': u.usertype
                    }
        users_list.append(user_dict)

    return jsonify(users_list)

@app.route('/remove-user', methods = ['POST'])
@login_required
def remove_user():
    #u = User.query.filter_by(username=request.form['username'])
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
    base_tasks = Base_Task.query.all()
    for task in base_tasks:
        if task.comments == None:
            task.comments = ''
        task.time = task.time.split('.')[0]
        if task.overdue is not None:
            task.overdue = task.overdue.split('.')[0]

        add_to_today = False
        todays_day = datetime.today().strftime('%A')
        if task.comments=='':
            add_to_today = True
        elif todays_day.lower() in task.comments.lower() and 'not '+task.comments.lower() not in task.comments.lower():
            add_to_today = True
        task = Todays_Task(date=date, time=task.time, shift=task.shift,
                           task=task.task, overdue=task.overdue,
                           comments=task.comments, assignee='',
                           completed=0, completed_date='',
                           completed_time='',completed_by='')
        db.session.add(task)
    db.session.commit()

    return render_template('user_page.html')

@app.route('/')
@app.route('/index')
@app.route('/user-page')
@login_required
def index():
    return render_template('user_page.html')

@app.route('/get-todays-tasks')
@login_required
def todays_tasks():
    tasks = Todays_Task.query.all()
    all_tasks_dict = {}
    todays_tasks_list = []
    for task in tasks:
        task_dict = {
                    'id': task.id,
                    'date': task.date,
                    'time': task.time,
                    'shift': task.shift,
                    'task': task.task,
                    'completed': task.completed,
                    'assignee': task.assignee,
                    'overdue': task.overdue,
                    'comment': task.comments
                    }
        todays_tasks_list.append(task_dict)


    my_tasks_list = []
    username = current_user.get_username()
    my_tasks = Todays_Task.query.filter_by(assignee=username).all()
    for task in my_tasks:
        task_dict = {
                    'id': task.id,
                    'date': task.date,
                    'time': task.time,
                    'shift': task.shift,
                    'task': task.task,
                    'completed': task.completed,
                    'assignee': task.assignee,
                    'overdue': task.overdue,
                    'comment': task.comments
                    }
        my_tasks_list.append(task_dict)

    all_tasks_dict['todays_tasks'] = todays_tasks_list
    all_tasks_dict['my_tasks'] = my_tasks_list

    return jsonify(all_tasks_dict)

@app.route('/assign-item', methods=['POST'])
@login_required
def assign_item():
    data = json.loads(request.data)
    task = Todays_Task.query.filter_by(id=data['item_id']).first()
    task.assignee = current_user.get_username()
    db.session.commit()

    task_dict = {
                'id': task.id,
                'date': task.date,
                'time': task.time,
                'shift': task.shift,
                'task': task.task,
                'completed': task.completed,
                'assignee': task.assignee,
                'overdue': task.overdue,
                'comment': task.comments
                }
    socketio.emit('assign', {'id': task.id, 'assignee': task.assignee})

    return jsonify(task_dict)

@app.route('/unassign-item/<item_id>')
@login_required
def unassign_item(item_id):
    task = Todays_Task.query.filter_by(id=item_id).first()
    task.assignee = ""
    db.session.commit()

    data = {'id': item_id}
    socketio.emit('unassign', {'id': item_id})
    return jsonify(data)




@app.route('/complete-item/<item_id>/<shift>/')
@login_required
@socketio.on('completed')
def complete_item(item_id, shift):
    task = Todays_Task.query.filter_by(id=item_id).first()
    task.completed = 1

    db.session.commit()

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
