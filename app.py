# ./app.py


from flask import Flask, flash, redirect, render_template, request, session, abort, g, jsonify, url_for
import json
import sqlite3
import os
from datetime import datetime
from flask_socketio import SocketIO
from datetime import datetime
# create flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'


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

# index route, shows index.html view
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/base_tasks')
def base_tasks():
    print("got session useranem", session['username'])
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
    cur.execute(sql, (data['time'], data['shift'], data['task'], data['assignee'], data['overdue'], data['comment'], data['completed']))
    conn.commit()

    # query to get task id
    sql = 'select id from base_tasks where time=="%s" and task=="%s"' % (data['time'], data['task'])
    id = cur.execute(sql)
    data['id'] = id.fetchone()[0]


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

@app.route('/user-page')
def user_page():

    return render_template('user_page.html')

@app.route('/get-todays-tasks')
def todays_tasks():
    print('here', session['username'])
    conn = get_db()
    cur = conn.cursor()
    sql = 'select * from todays_tasks where date=="%s"' % (datetime.now().strftime("%Y-%m-%d"))
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

    sql = 'select * from todays_tasks where date=="%s" and assignee=="%s"' % (datetime.now().strftime("%Y-%m-%d"), session.get('username'))
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
def assign_item():
    data = json.loads(request.data)

    item_id = data['item_id']
    conn = get_db()
    cur = conn.cursor()
    print('>>>>>>>>>>>>', session.get(''))
    sql = 'update todays_tasks set assignee = "%s" where id=="%s"' % (session.get('username'), item_id)
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


@app.route('/complete-item/<item_id>')
@socketio.on('completed')
def complete_item(item_id):
    print("completing", item_id)
    conn = get_db()
    cur = conn.cursor()
    sql = 'update todays_tasks set completed = "%s" where id == "%s"' % (1,item_id)
    cur.execute(sql)
    conn.commit()
    data = {'id': item_id}
    socketio.emit('completed', {'id': item_id})
    return jsonify(data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    session['username'] = 'fred'
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        sql = 'select username,password,firstname,lastname from users where username == "%s"' % request.form['username']
        cur.execute(sql)
        user_values = cur.fetchone()

        if user_values is None:
            error = 'Invalid credentials'
            return render_template('index.html', error=error)
        user = {'username': user_values[0],
                'password': user_values[1],
                'firstname': user_values[2],
                'lastname': user_values[3]}
        if request.form['username'] != user['username'] or \
                request.form['password'] != user['password']:
            error = 'Invalid credentials'
        else:
            session['logged_in'] = True
            session['name'] = user['firstname'] + ' ' + user['lastname']
            session['username'] = user['username']
            print("set session useranem", session['username'])
            return redirect(url_for('base_tasks'))
    return render_template('index.html', error=error)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

from flask import send_from_directory

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    # run Flask app in debug mode
    #app.secret_key = os.urandom(12)
    #app.run(debug=True)

    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
