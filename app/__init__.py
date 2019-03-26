from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from flask_socketio import SocketIO
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
#socket = SocketIO(app)

login.login_view = 'login'
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
from app import routes, models
