import psycopg2
import pandas as pd
from sqlalchemy import create_engine
#import csv
import os

s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conndict = dict(item.split("=") for item in s.split(" "))
connstring = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
engine=create_engine(connstring)
print(connstring)
print(conndict)
#conn = psycopg2.connect(os.environ["AZURE_POSTGRESQL_CONNECTIONSTRING"])
        #host="localhost",
        #database="gwtroll-database",
        #user=os.environ["DB_USERNAME"],
        #password=os.environ["DB_PASSWORD"])

#cur = conn.cursor()


### Import data from CSV
""" with open('./import.csv', 'r') as f:
    # Notice that we don't need the csv module
    next(f) # Skip the header row.
    cur.copy_expert('COPY registrations (fname, lname, scaname, lodging) FROM stdin WITH CSV', f)
    #cur.copy_from(f, 'registrations', sep=',', columns=['fname', 'lname', 'scaname', 'lodging'])

conn.commit()
conn.close() """

df = pd.read_csv('gwpricing.csv')
print(df)

try:
    df.to_sql('pricing', engine, if_exists= 'replace', index= False)

except:
    print("Sorry, some error has occurred!")

finally:
    engine.dispose()

