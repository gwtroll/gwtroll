import psycopg2
#import csv
import os

conn = psycopg2.connect(os.environ["AZURE_POSTGRESQL_CONNECTIONSTRING"])
        #host="localhost",
        #database="gwtroll-database",
        #user=os.environ["DB_USERNAME"],
        #password=os.environ["DB_PASSWORD"])

cur = conn.cursor()

### Query DB
Users = cur.execute('SELECT * FROM users;')
print(Users)
Roles = cur.execute('SELECT * FROM roles;')
print(Roles)

conn.commit()
conn.close()