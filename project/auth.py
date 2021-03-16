# auth.py
from datetime import datetime
from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from .email import send_email
from . import Config

auth = Blueprint('auth', __name__, url_prefix='/user')


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))  # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    if not user.confirmed:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Please activate your email address')
        return redirect(url_for('auth.login'))
    return redirect(url_for('content.template_test'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


def generate_confirmation_token(email):
    app = Flask(__name__)
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt=Config.SECURITY_PASSWORD_SALT)


def confirm_token(token, expiration=3600):
    app = Flask(__name__)
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        print(Config.SECURITY_PASSWORD_SALT)
        email = serializer.loads(
            token,
            salt=Config.SECURITY_PASSWORD_SALT,
            max_age=expiration
        )
    except:
        return False
    return email


@auth.route('/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(
        email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email,
                    name=name,
                    password=generate_password_hash(password, method='sha256'),
                    registered_on=datetime.now(),
                    confirmed=False)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    token = generate_confirmation_token(new_user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(new_user.email, subject, html)

    login_user(new_user)

    flash('A confirmation email has been sent via email.', 'success')

    return redirect(url_for('auth.login'))


@auth.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')

    email = confirm_token(token)
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('content.template_test'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('content.template_test'))
