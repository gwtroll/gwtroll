import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
    conndict = dict(item.split("=") for item in s.split(" "))
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
    print(SQLALCHEMY_DATABASE_URI)