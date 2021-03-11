import json
from flask import redirect, render_template, url_for, flash, request, Response, jsonify
from flask_login import login_user, login_required, current_user, logout_user
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from main import db, login_manager, app, mail
from main.forms import RegisterForm, LoginForm, NewDestinationForm, MyAccountForm, ContactForm, RequestTokenForm, ResetPasswordForm
from main.models import Users, Destinations
from main.utils import cities, get_iata_code, get_flights_data
from main.offer import SendFlightOffer


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    return Response(json.dumps(cities), mimetype='application/json')


@app.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        user_cities = Destinations.query.filter_by(
            user_id=current_user.id).all()
        cities_db = [item.name for item in user_cities]
        form = NewDestinationForm()
        if form.validate_on_submit():
            if form.destination.data not in cities:
                flash(f"{form.destination.data} is not in the list")
            elif form.destination.data in cities_db:
                flash(f"{form.destination.data} is already in the list")
            else:
                new_dest = Destinations(
                    name=form.destination.data,
                    iata_code=get_iata_code(form.destination.data),
                    min_no_days=7,
                    max_no_days=28,
                    max_price=0,
                    user_id=current_user.id
                )
                db.session.add(new_dest)
                db.session.commit()
            return redirect(url_for('home'))
        return render_template('home.html', form=form, user_cities=user_cities)
    else:
        return render_template('home.html')


@ app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        check_user = Users.query.filter_by(email=form.email.data).first()
        if check_user:
            flash("This email already exists in our database. Please login!")
            return(redirect(url_for('login')))
        new_user = Users(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            home_city="Bucharest",
            home_iata="OTP"
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@ app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if not user:
            flash("This email doesn't exist in our database. Please register first!")
            return redirect(url_for('register'))
        elif check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Incorrect email or password!")
    return render_template('login.html', form=form)


@ app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@login_required
@app.route('/account', methods=['GET', 'POST'])
def account():
    form = MyAccountForm()
    user = Users.query.filter_by(id=current_user.id).first()
    if form.validate_on_submit():
        check_user = Users.query.filter_by(username=form.username.data).first()
        check_email = Users.query.filter_by(username=form.email.data).first()
        if check_user or check_email:
            form.username.data = user.username
            form.email.data = user.email
            flash("Username or email is already taken!")
        else:
            user.username = form.username.data
            user.email = form.email.data
            user.home_city = form.home_city.data
            user.home_iata = get_iata_code(form.home_city.data)
            db.session.commit()
            return redirect(url_for('home'))
    else:
        form.username.data = user.username
        form.email.data = user.email
        form.home_city.data = user.home_city
    return render_template('account.html', form=form)


@ app.route('/delete-city/<int:city_id>', methods=['GET', 'DELETE'])
def delete_city(city_id):
    city = Destinations.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/update-city/<int:city_id>', methods=['GET', 'POST'])
def update_city(city_id):
    city = Destinations.query.filter_by(id=city_id).first()
    if city:
        city.max_price = request.form.get('price')
        city.min_no_days = request.form.get('min-days')
        city.max_no_days = request.form.get('max-days')
        db.session.commit()
        return redirect(url_for('home'))
    else:
        flash("Something went wrong")


@app.route('/get-offer')
@login_required
def get_offer():
    with app.app_context():
        user = Users.query.filter_by(id=current_user.id).first()
        offer = SendFlightOffer(user)
        offer.create_email_form()
        flash("The offer has been sent. Please check your email")
    return redirect(url_for('home'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        full_message = f"""{form.fullname.data}<br>
{form.email.data}<br>
{form.subject.data}<br>
{form.content.data}
        """
        msg = Message('Contact Form Filled', sender="testpythonemail3@gmail.com",
                      recipients=[PERSONAL_EMAIL])
        msg.body = "Contact Form"
        msg.html = full_message
        mail.send(msg)
        flash("You're message has been sent! Thank you for your feedback")
        return redirect(url_for('home'))
    elif current_user.is_authenticated:
        form.email.data = current_user.email
    return render_template('contact.html', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset', sender="testpythonemail3@gmail.com",
                  recipients=[user.email])
    msg.body = "Password Reset"
    msg.html = f"""To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}
    """
    mail.send(msg)


@app.route('/request-token', methods=['GET', 'POST'])
def request_token():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestTokenForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash("An email with reset instruction has been sent to your address.")
            return redirect(url_for('login'))
        else:
            flash("This email doesn't exist in our database. Please register!")
            return redirect(url_for('register'))
    return render_template('request_token.html', form=form)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Users.verify_token(token)
    if user is None:
        flash('This is an invalid or expired token.')
        return redirect(url_for('request_token'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash("Your password has been updated.")
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')
