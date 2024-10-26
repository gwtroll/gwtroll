import uuid
import psycopg2
import pandas as pd
import sqlalchemy as db
import os

s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conndict = dict(item.split("=") for item in s.split(" "))
connstring = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
engine=db.create_engine(connstring)
#conn = engine.connect()
metadata = db.MetaData()
registrations = db.Table('registrations', metadata)

conn = psycopg2.connect(os.environ["AZURE_POSTGRESQL_CONNECTIONSTRING"])
cur = conn.cursor()

cur.execute('DELETE FROM public.users')

conn.commit()

cur.execute('INSERT INTO public.users (id, username, fname, lname, active, fs_uniquifier) VALUES (1, %s, %s, %s, true, %s);',("admin","admin","admin",uuid.uuid4().hex))

conn.commit()

cur.execute('INSERT INTO public.user_roles (id, user_id, role_id) VALUES (1, 1, 1);')

conn.commit()
conn.close()

# print("Roles Created")

# with app.app_context():
#     if User.query.filter_by(id=1).first() is None:
#         admin = User(id=1, username='admin', roles=[Role.query.filter_by(id=1).first()], fname='Admin', lname='Admin', fs_uniquifier=uuid.uuid4().hex, active=True)
#         admin.set_password("admin")
#         try:
#             db.session.add(admin)
#             db.session.commit()
#             db.session.close()
#         except:
#             print('Could Not Commit Admin')

#         print("Admin Created")