import psycopg2
#import csv
import os

conn = psycopg2.connect(os.environ["AZURE_POSTGRESQL_CONNECTIONSTRING"])
        #host="localhost",
        #database="gwtroll-database",
        #user=os.environ["DB_USERNAME"],
        #password=os.environ["DB_PASSWORD"])

cur = conn.cursor()

### Create Table

cur.execute('DROP TABLE IF EXISTS registrations;')

cur.execute('CREATE TABLE registrations'
    '(id SERIAL PRIMARY KEY,'
    'fname TEXT NOT NULL,'
    'lname TEXT NOT NULL,'
    'scaname TEXT,'
    'lodging TEXT NOT NULL,'
    'regdate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,'
    'checkin TIMESTAMP,'
    'regid INTEGER,'
    'medallion INTEGER);'
    )


conn.commit()
conn.close()