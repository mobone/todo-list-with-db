from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    firstname = db.Column(db.String(120), index=True)
    lastname = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    usertype = db.Column(db.String(64))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_username(self):
        return self.username

    def get_admin(self):
        if self.usertype == "Admin":
            return True
        else:
            return False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Base_Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(70))
    shift = db.Column(db.String(30))
    task = db.Column(db.String(350))
    overdue = db.Column(db.String(70))
    comments = db.Column(db.String(350))


class Todays_Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(70))
    time = db.Column(db.String(70))
    shift = db.Column(db.String(30))
    task = db.Column(db.String(350))
    overdue = db.Column(db.String(70))
    comments = db.Column(db.String(350))
    assignee = db.Column(db.String(100))
    completed = db.Column(db.Integer)
    completed_date = db.Column(db.String(70))
    completed_time = db.Column(db.String(70))
    completed_by = db.Column(db.String(100))

class Archived_Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    time = db.Column(db.DateTime)
    shift = db.Column(db.String(30))
    task = db.Column(db.String(350))
    overdue = db.Column(db.DateTime)
    comments = db.Column(db.String(350))
    assignee = db.Column(db.String(100))
    completed = db.Column(db.Integer)
    completed_date = db.Column(db.DateTime)
    completed_time = db.Column(db.DateTime)
    completed_by = db.Column(db.String(100))
