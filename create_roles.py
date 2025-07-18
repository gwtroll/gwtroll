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

cur.execute('DELETE from public.roles;')

conn.commit()

cur.execute('INSERT INTO public.roles (id, name) VALUES (1, %s), (2, %s), (3, %s), (4, %s), (5, %s), (6, %s), (7, %s), (8, %s), (9, %s), (10, %s), (11, %s);',("Admin","Troll Shift Lead","Troll User","Marshal Admin","Marshal User","Land","Invoices","Cashier","Department Head", "Merchant Head", "Autocrat"))
#cur.execute('INSERT INTO public.roles (id, name) VALUES (%s, %s);',("9", "Royal Liasion"))

conn.commit()
conn.close()

print("Roles Created")