import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING'] = "host=localhost dbname=postgres user=postgres password=IAmTheDoctor!"
    # s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
    # conndict = dict(item.split("=") for item in s.split(" "))
    # SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 

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
    # MAIL_USERNAME = 
    # MAIL_PASSWORD = gmail_app_password
    MAIL_DEFAULT_SENDER = None
    MAIL_MAX_EMAILS = None
    MAIL_SUPPRESS_SEND = False
    aMAIL_ASCII_ATTACHMENTS = False