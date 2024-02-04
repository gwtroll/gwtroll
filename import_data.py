import psycopg2
#import csv
import os

conn = psycopg2.connect(
        host="localhost",
        database="gwtroll-database",
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"])

cur = conn.cursor()


### Import data from CSV
with open('./import.csv', 'r') as f:
    # Notice that we don't need the csv module
    next(f) # Skip the header row.
    cur.copy_expert('COPY registrations (fname, lname, scaname, lodging) FROM stdin WITH CSV', f)
    #cur.copy_from(f, 'registrations', sep=',', columns=['fname', 'lname', 'scaname', 'lodging'])

conn.commit()
conn.close()