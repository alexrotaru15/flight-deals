import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_moment import Moment

login_manager = LoginManager()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "sqlite:///blog.db")
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['SECURITY_EMAIL_SENDER'] = os.environ.get('SECURITY_EMAIL_SENDER')
PERSONAL_EMAIL = os.environ.get('PERSONAL_EMAIL')
mail = Mail(app)
moment = Moment(app)

mail.init_app(app)
login_manager.init_app(app)
moment.init_app(app)

from main import routes
