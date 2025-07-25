import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    database_url = os.environ('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://')
    SQLALCHEMY_DATABASE_URI = database_url
    # rest of connection code using the connection string `uri`
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEBUG = True
    MAIL_DEFAULT_SENDER = None
    MAIL_MAX_EMAILS = None
    MAIL_SUPPRESS_SEND = False
    aMAIL_ASCII_ATTACHMENTS = False