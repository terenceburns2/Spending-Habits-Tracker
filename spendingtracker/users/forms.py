from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from spendingtracker.models import User


# Used in 'register' page for users to register new account
class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # To validate form field, create functions in this format:
    # validate_field(self, field) where field is the field name in the from

    # Verify if the email is already in the database
    # If yes, then raise an error message
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    # Verify if the phone is already in the database
    # If yes, then raise an error message
    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('That phone is taken. Please choose a different one.')


# Used in 'login' page for users to login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# Used in 'reset_password' page for users to send email to their email address
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Email')

    # Validate if the email is existed in db
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with this email. Please use a valid email.")


# Used in 'reset_password/<token>' page for users to reset password
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update')


# Used in 'settings' page for users to change account information
class SettingsForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    budget = BooleanField('Receive Budget Emails:')
    balance = BooleanField('Receive Balance Emails:')
    report =BooleanField('Receive Report Emails:')
    save = SubmitField('Save')

    # Verify if the email is already in the database
    # If yes, then raise an error message
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user != current_user:
            raise ValidationError('That email is taken. Please choose a different one.')

    # Verify if the phone is already in the database
    # If yes, then raise an error message
    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user and user != current_user:
            raise ValidationError('That phone is taken. Please choose a different one.')