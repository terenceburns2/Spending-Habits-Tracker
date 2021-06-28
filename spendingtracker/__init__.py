from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from spendingtracker.config import Config



db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'  # 'login' is the function name of routes.py, if the user wants to access to a page that requires login, he will be took to login page.
login_manager.login_message_category = 'info'
mail = Mail()



# Factory pattern
def create_app(config_class=Config):
    # Create instances here so that other scripts can import them
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # import the instance of blueprints
    from spendingtracker.users.routes import users
    from spendingtracker.cards.routes import cards
    from spendingtracker.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(cards)
    app.register_blueprint(main)

    return app