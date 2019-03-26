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
