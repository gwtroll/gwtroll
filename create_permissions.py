import psycopg2
import pandas as pd
import sqlalchemy as db
#import csv
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

cur.execute('DELETE from public.permissions;')

conn.commit()

cur.execute('INSERT INTO public.permissions (id, name) VALUES (1, %s), (2, %s), (3, %s), (4, %s), (5, %s), (6, %s), (7, %s), (8, %s), (9, %s), (10, %s), (11, %s), (12, %s), (13, %s), (14, %s), (15, %s), (16, %s);',("admin","view_users","edit_users","earlyon_view","earlyon_edit","invoice_view","invoice_edit","marshal_view","marshal_edit","marshal_reports","merchant_view","merchant_edit","merchant_reports","registration_view","registration_edit","registration_reports"))
#cur.execute('INSERT INTO public.roles (id, name) VALUES (%s, %s);',("9", "Royal Liasion"))

conn.commit()
conn.close()

print("Permissions Created")