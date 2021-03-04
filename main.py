import os
from flask import Flask, redirect, render_template, url_for, flash
from forms import RegisterForm, LoginForm, NewDestinationForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_mail import Mail, Message

login_manager = LoginManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flights.db'
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    cities = relationship("Destinations")


class Destinations(db.Model):
    __tablename__ = "destinations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    iata_code = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# db.create_all()

# def send_email():
#     msg = Message('Sal', sender="testpythonemail3@gmail.com",
#                   recipients=["alexrotaru1595@gmail.com"])
#     msg.body = "Testing"
#     msg.html = "test"
#     mail.send(msg)


@app.route('/', methods=['GET', 'POST'])
def home():
    form = NewDestinationForm()
    if form.validate_on_submit():
        pass
    return render_template('home.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        check_user = Users.query.filter_by(email=form.email.data).first()
        if check_user:
            flash("This email already exists in our database. Please login!")
            return(redirect(url_for('login')))
        new_user = Users(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if not user:
            flash("This email doesn't exist in our database. Please register first!")
            return redirect(url_for('register'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
