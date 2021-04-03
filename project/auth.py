# auth.py
from datetime import datetime, timedelta
from smtplib import SMTPException

from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db, Config
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from .email_send import send_email
from project import recaptcha

auth = Blueprint('auth', __name__, url_prefix='/user')

@auth.route('/resend')
def resend():
    return render_template('resend.html')

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/resend', methods=['POST'])
def resend_post():
    #if recaptcha.verify():
    #    pass
    #else:
    #    flash('Captcha is wrong.')
    #    return redirect(url_for('auth.login'))
    email = request.form.get('email')
    print(email)
    user = User.query.filter_by(
        email=email).first()  # if this returns a user, then the email already exists in database

    if not user:  # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('auth.signup'))

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user:
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.signup'))  # if user doesn't exist or password is wrong, reload the page

    if not user.confirmed:
        email_send_time = user.confirm_email_send_at
        #email_send_time_date = datetime.strptime(email_send_time, '%Y-%m-%d %H:%M:%S.%f')
        delta_email_send_time = (datetime.now() - email_send_time)

        if delta_email_send_time.total_seconds() < 180:

            email_can_send_time = (email_send_time + timedelta(minutes=3))
            delta_can_send_time = (email_can_send_time - datetime.now())

            flash('The next email can be sent in ' + str(delta_can_send_time.total_seconds()).split(".", 1)[0] + ' seconds, please try again later')
            return redirect(url_for('auth.resend'))
        else:

            token = generate_confirmation_token(user.email)
            confirm_url = url_for('auth.confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            try:
                send_email(user.email, subject, html)
                user.confirm_email_send_at = datetime.now()
                db.session.add(user)
                db.session.commit()
                flash("The email has been sent! Don't forget to check the spam folder")
            except SMTPException:
                flash('We have some problems with sending emails. Please try again later :(')
                return redirect(url_for('auth.resend'))



            return redirect(url_for('auth.resend'))

    #return redirect(url_for('auth.resend'))

    return redirect(url_for('content.template_test'))


@auth.route('/login', methods=['POST'])
def login_post():
    #if recaptcha.verify():
    #    pass
    #else:
    #    flash('Captcha is wrong.')
    #    return redirect(url_for('auth.login'))

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
    if not user.confirmed:  # if a user is found, we want to redirect back to signup page so user can try again
        ## Здесь нужно сделать редирект на страницу переотправки
        flash('You need to confirm your email. You can send it again by specifying the mail during registration')
        return redirect(url_for('auth.resend'))
    login_user(user, remember=remember)
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
                    confirm_email_send_at=datetime.now(),
                    confirmed=False)

    token = generate_confirmation_token(new_user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    try:
        maildebug = send_email(new_user.email, subject, html)
        print(maildebug)
        flash('A confirmation email has been sent via email.', 'success')
    except SMTPException:
        flash('We have some problems with sending emails. Please try again later :(')
        return redirect(url_for('auth.signup'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    #login_user(new_user)

    return redirect(url_for('auth.login'))


@auth.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        redirect(url_for('auth.resend'))

    email = confirm_token(token)
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
        redirect(url_for('auth.login'))
    else:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Please login.', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('content.template_test'))
