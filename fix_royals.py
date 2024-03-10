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


### Import data from CSV

df = pd.read_csv('royal_regid.csv')
# Rename columns from CSV to match DB - order is important
df.columns = ['regid']

conn = psycopg2.connect(os.environ["AZURE_POSTGRESQL_CONNECTIONSTRING"])
cur = conn.cursor()
regids=[]

for index, row in df.iterrows():
    regid = int(row['regid'])
    print(regid)
    cur.execute('UPDATE registrations SET rate_age = %s WHERE regid = %s;', ("Royals", regid))


conn.commit()
conn.close()


""" except:
    print("Sorry, some error has occurred!")

finally:
    engine.dispose()

 """