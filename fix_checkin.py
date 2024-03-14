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



cur.execute('UPDATE registrations SET checkin = (checkin - %s::interval) WHERE checkin BETWEEN TO_TIMESTAMP(%s,%s) AND TO_TIMESTAMP(%s,%s);', ("5 hours", "2024-03-10 02:00:01", "YYYY-MM-DD HH24:MI:SS", "2024-03-13 01:00:00", "YYYY-MM-DD HH24:MI:SS"  ))


conn.commit()
conn.close()


""" except:
    print("Sorry, some error has occurred!")

finally:
    engine.dispose()

 """