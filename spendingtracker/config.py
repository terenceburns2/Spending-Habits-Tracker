
class Config:
    SECRET_KEY = 'd14634e312b76f3fc47e98af4cf9e69d'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    # Gmail information:
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'GRPT1SpendingTracker@gmail.com'
    MAIL_PASSWORD = 'GRPTeam1'
    # MAIL_USERNAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
