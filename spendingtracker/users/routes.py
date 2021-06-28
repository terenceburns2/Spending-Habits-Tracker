from flask import render_template, url_for, flash, redirect, request, Blueprint, session, current_app
from spendingtracker import db, bcrypt
from spendingtracker.users.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, SettingsForm
from spendingtracker.common.senders import send_reset_email
from spendingtracker.models import User, Log, LogSchema
from flask_login import login_user, current_user, logout_user, login_required
from datetime import timedelta, datetime
from spendingtracker.common.utils import flash_message
from spendingtracker.users.utils import get_latest_login, get_ip_address


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register the client.
    If an authenticated user tries to access this page, he/she will be redirected to homepage.
    If the client successfully registered, he will be redirected to login and regarded as successful login.
    Specifically, when a client successfully registered, a User object will be created and filled in with the
    information he provided in the register form. Client's password will be hashed and saved in the database and
    no one can access to it. Then the website will record the client's ip address, login time and login email.
    When the user logs out, the website will record his/her logout time and keep the log in the database.
    """
    # If the current user is already logged in, redirect to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))
    # Create an instance of the registration form for displaying
    form = RegistrationForm()
    if form.validate_on_submit():
        # If all requirements are satisfied and the user click on the 'submit' (the form is sent to the same url):
        # Hashing password
        # Bcrypt will add a random salt automatically, so there is no need to set the salt here
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
        user = User(firstname=form.firstname.data,
                    lastname=form.lastname.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # Flash messages can be passed between pages, message tag is placed in 'layout.html'
        flash_message(f'Account created for {form.email.data}!', 'success', user.id)
        login_user(user)
        next_page = request.args.get('next')  # http://127.0.0.1:5000/login?next=%2Faccount
        (ip, region) = get_ip_address(request)
        log = Log(email=form.email.data,
                  ip=ip,
                  login=datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"),
                  region=region,
                  owner=user)
        db.session.add(log)
        db.session.commit()
        # Set the duration of login session
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(minutes=5)
        return redirect(url_for('main.homepage'))
        # render_template('login.html', title='Login')
    # otherwise, the user is accessing this page with 'GET', just display the register.html
    return render_template('register.html', title='Register', form=form)



@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                (ip, region) = get_ip_address(request)
                next_page = request.args.get('next')  # http://8.208.24.109/login?next=%2F
                log = Log(email=form.email.data,
                          ip=ip,
                          login=datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"),
                          region=region,
                          owner=user)
                db.session.add(log)
                db.session.commit()
                # Set the duration of login session
                session.permanent = True
                current_app.permanent_session_lifetime = timedelta(minutes=5)
                return redirect(next_page) if next_page else redirect(url_for('main.homepage'))
            else:
                flash('Invalid Password. Please check your password', 'danger')
        else:
            # flash messages can be passed between pages, message tag is placed in 'layout.html'
            flash('Account doesn\'t exist. Please check email', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
@login_required
def logout():
    """
    When the user click on 'logout', his logout information (time) will be recorded in the database.
    """
    log = get_latest_login(current_user)
    if log is not None:
        log.logout = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        db.session.commit()
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Create the settings form with current user's information
    form = SettingsForm(email=current_user.email, phone=current_user.phone)
    if form.validate_on_submit():
        # Update email
        if form.email != current_user.email:
            current_user.email = form.email.data
        # Update phone
        if form.phone != current_user.phone:
            current_user.phone = form.phone.data
        # # Update password
        if form.password.data != "":
            # Hash password
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
            # Save hashed password
            current_user.password = hashed_password
        current_user.preference.balance = form.balance.data
        current_user.preference.budget = form.budget.data
        current_user.preference.report = form.report.data
        db.session.commit()
        # flash messages can be passed between pages, message tag is placed in 'layout.html'
        # flash(f'Your settings have been updated!', 'success')
        flash_message(f'Your settings have been updated!', 'success', current_user.id)
        return redirect(url_for('main.homepage'))
    logs = current_user.logs
    logs_schema = LogSchema()
    listOfDict = []
    for log in logs:
        dict_log = logs_schema.dump(log)
        listOfDict += [dict_log]
    return render_template('settings.html', title='Settings', form=form, logs_json=listOfDict)



@users.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        # flash messages can be passed between pages, message tag is placed in 'layout.html'
        # flash('An email has been set with instructions to reset your password', 'info')
        flash_message('An email has been set with instructions to reset your password', 'info', user.id)
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', title='Reset Password', form=form)



@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))
    user = User.verify_reset_token(token)
    if user is None:
        # flash messages can be passed between pages, message tag is placed in 'layout.html'
        flash('That is a invalid or expired token.', 'warning')
        return redirect(url_for('users.reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Adding user into database:
        #   1. First hash the password in got from the form
        #   2. Create a User instance
        #   3. Add the User instance into database
        #   4. Commit the change
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
        user.password = hashed_password
        # No need to add the user to db since the user is already in the db, we just update its password
        db.session.commit()
        # flash messages can be passed between pages, message tag is placed in 'layout.html'
        # flash(f'Your password has been updated! You are now able to login', 'success')
        flash_message(f'Your password has been updated! You are now able to login', 'success', user.id)
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
