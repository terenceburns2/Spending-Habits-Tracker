from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from spendingtracker import db, login_manager, ma
from flask_login import UserMixin
from flask import current_app
from spendingtracker.cards.utils import get_UUID, get_amount, get_currency, get_datetime, get_desctiption, classify_transaction
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True , nullable=False)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # in Card table, user will be marked/saved as 'owner'
    # lazy=True: SQLAlchemy will load data when necessary in one go
    # One User can have multiple bank Card(s); one-to-many
    cards = db.relationship('Card', backref='owner', lazy=True)
    # One User can have serveral website Message(s); one-to-many
    messages = db.relationship('Message', backref='owner', lazy=True)
    logs = db.relationship('Log', backref='owner', lazy=True)
    categorybudgets = db.relationship('Categorybudget', backref='owner', lazy=True)
    # 'uselist=False' means User and e.g. Spending table has one-to-one relationship, i.e. one user can only have one spending setting
    # 'uselist=True' is default, which means User and another table has one-to-many relationship, i.e. one user can have several e.g. cards
    # One User can only have one Spending (habit/record); one-to-one
    spending = db.relationship('Spending', backref='owner', lazy=True, uselist=False)
    # One User can only have one Preference (email services); one-to-one
    preference = db.relationship('Preference', backref='owner', lazy=True, uselist=False)

    def __init__(self, firstname, lastname, email, phone, password):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = password
        # User and Spending or Preference have one-to-one relationship, so they have to be created
        # when the user is created
        self.spending = Spending()
        self.preference = Preference()

    # Generates a token based on the SECRET_KEY and user ID with a expiry time of 1800s
    def get_reset_token(self, expires_sec=1800):
        # Create an instance of Serializer
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        # Return the token based on the user's id so that only the particular user can pass the verification
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        # Create a same instance of Serializer as the one created in 'get_reset_token' method
        # by using the app's 'SECRET_KEY'
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # Via the token, get the user id
            user_id = s.loads(token)['user_id']
        except:
            # If the token is invalid or there is no such an user
            # Return None
            return None
        return User.query.get(user_id)

    # how an object is printed when using 'print'
    def __repr__(self):
        return f"User(ID:'{self.id}', First name:'{self.firstname}', Email:'{self.email}')"


# Each card is related to one user, each user can have multiple cards
class Card(db.Model):

    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    sort_code = db.Column(db.String(20), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    card_name = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=1000.00)
    # One Card can have many transactions; one-to-many
    transactions = db.relationship('Transaction', backref='card', lazy=True)
    # Notice: 'user.id' is referencing to the table name 'user' and column name 'id'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, sort_code, account_number, card_name, balance, owner):
        self.sort_code = sort_code
        self.account_number = account_number
        self.card_name = card_name
        self.balance = balance
        self.owner = owner

    # Update card balance
    # If the balance is sufficient, then minus the transaction and return True;
    # Otherwise, return False and do nothing.
    def check_update_balance(self, transaction):
        if self.balance - transaction.amount < 0:
            return False
        else:
            self.balance = round(self.balance - transaction.amount, 2)
            return True

    # Get total card spending
    def get_total_spending(self):
        totalSpending = 0
        for transaction in self.transactions:
            if transaction.timestamp.month == datetime.utcnow().month:
                totalSpending += transaction.amount
        return round(totalSpending, 2)

    # how an object is printed when using 'print'
    def __repr__(self):
        return f"Card(Owner:'{self.owner.firstname}', ID:'{self.id}', Card Name:'{self.card_name}', Account Number:'{self.account_number}', Sort Number:'{self.sort_code}', Balance:'{self.balance}')"


# Each transaction is related to one card, each card can have multiple transactions
class Transaction(db.Model):

    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    transactionUUID = db.Column(db.String(50), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General')
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)

    # Generate a random transaction
    def __init__(self, card_id):
        self.transactionUUID = get_UUID()
        self.amount = get_amount()
        self.currency = get_currency()
        self.timestamp = get_datetime()
        self.description = get_desctiption()
        self.category = classify_transaction(self.description)
        self.card_id = card_id

    # how an object is printed when we print it out
    def __repr__(self):
        return f"Transaction(ID:'{self.id}', TransactionUUID:'{self.transactionUUID}', Time:'{self.timestamp}', Description:'{self.description}', Amount:'{self.currency}{self.amount}', Category:'{self.category}', CardID:'{self.card_id}')"


# User login log: stores user email, login ip address, login time and logout time (not yet implemented)
class Log(db.Model):

    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    login = db.Column(db.String(50), nullable=False)
    logout = db.Column(db.String(50), nullable=True)
    ip = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # how an object is printed when using 'print'
    def __repr__(self):
        return f"Log(User:'{self.email}', IP:'{self.ip}', Login Time:'{self.login}', Region:'{self.region}')"


# User budget, update time and total spending
class Spending(db.Model):

    __tablename__ ='spending'
    id = db.Column(db.Integer, primary_key=True)
    budget = db.Column(db.Float)
    budget_set_timestamp = db.Column(db.DateTime)
    # Default currency is GBP
    totalAccountSpending = db.Column(db.Float, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def update_spending(self):
        self.totalAccountSpending = 0
        for card in self.owner.cards:
            self.totalAccountSpending += card.get_total_spending()
        round(self.totalAccountSpending, 2)

    def check_spending(self):
        if (self.budget != '' and self.budget != None) and self.totalAccountSpending >= self.budget:
            return True
        else:
            return False

    # how an object is printed when using 'print'
    def __repr__(self):
        return f"Spending(Owner:'{self.owner.firstname}', Budget:'{self.budget}', Budget Update:'{self.budget_set_timestamp}', Total Spending:'{self.totalAccountSpending}'"


# Website messages
class Message(db.Model):

    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # how an object is printed when using 'print'
    def __repr__(self):
        return f"Message(User:'{self.owner.firstname}', Time:'{self.timestamp}', Type:'{self.type}', Content:'{self.content}')"


# User settings preference:
#   1. Budget email
#   2. Report email
class Preference(db.Model):

    __tablename__ = 'preference'
    id = db.Column(db.Integer, primary_key=True)
    budget = db.Column(db.Boolean, default=True, nullable=False)
    balance = db.Column(db.Boolean, default=True, nullable=False)
    report = db.Column(db.Boolean, default=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # how an object is printed when using 'print'
    def __repr__(self):
        return f"Preference(User:'{self.owner.firstname}', Receive Budget Email:'{self.budget}', Receive Balance Email:'{self.balance}', Receive Report Email:'{self.report}', Budget Counter:'{self.budget_counter}')"


class Categorybudget(db.Model):

    __tablename__ = 'categorybudget'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Category Budget(User:'{self.owner.firstname}', Category:'{self.category}', Budget:'￡{self.budget}')"


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

class CardSchema(ma.ModelSchema):
    class Meta:
        model = Card

class TransactionSchema(ma.ModelSchema):
    class Meta:
        model = Transaction

class LogSchema(ma.ModelSchema):
    class Meta:
        model = Log

class MessageSchema(ma.ModelSchema):
    class Meta:
        model = Message

class SpendingSchema(ma.ModelSchema):
    class Meta:
        model = Spending

class CategorybudgetSchema(ma.ModelSchema):
    class Meta:
        model = Categorybudget
