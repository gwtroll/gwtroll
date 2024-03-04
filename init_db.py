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
cur.execute('DROP TABLE IF EXISTS alembic_version;')

cur.execute('DROP TABLE IF EXISTS registrations;')

cur.execute('CREATE TABLE registrations'
    '(regid SERIAL PRIMARY KEY,'
    'order_id INTEGER,'
    'reg_date_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,'
    'medallion INTEGER,'
    'fname TEXT,'
    'lname TEXT,'
    'kingdom TEXT,'
    'event_ticket TEXT,'
	'rate_mbr TEXT,'
	'rate_age TEXT,'
	'rate_date TEXT,'
    'price_calc INTEGER,'
    'price_paid INTEGER,'
	'price_due INTEGER,'
    'lodging TEXT,'
    'pay_type TEXT,'
    'prereg_status TEXT,'
    'scaname TEXT,'
    'mbr_num_exp TEXT,'
    'mbr_num INTEGER,'
    'mbr_exp DATE,'
    'requests TEXT,'
    'checkin TIMESTAMP);'
    )

cur.execute ('ALTER SEQUENCE registrations_regid_seq RESTART WITH 60001;')
# cur.execute('DROP TABLE IF EXISTS pricing;')

# cur.execute('CREATE TABLE pricing'
#     '(arrdate DATE PRIMARY KEY,'
#     'arrday TEXT NOT NULL,'
#     'prereg_price INTEGER NOT NULL,'
#     'door_price INTEGER NOT NULL,'
#     'nmr INTEGER NOT NULL);'
#     )


conn.commit()
conn.close()