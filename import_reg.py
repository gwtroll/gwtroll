import psycopg2
import pandas as pd
import sqlalchemy as db
#import csv
import os

s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conndict = dict(item.split("=") for item in s.split(" "))
connstring = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
engine=db.create_engine(connstring)
conn = engine.connect()
metadata = db.MetaData()
registrations = db.Table('registrations', metadata)

pricing = db.Table('pricing', metadata)

price_df = pd.read_sql_table('pricing', conn)

### Import data from CSV

df = pd.read_csv('scores_export.csv')
# Rename columns from CSV to match DB - order is important
df.columns = ['event_id','event_name','order_id','reg_date_time','medallion','fname','lname','scaname_bad','acc_member_id','acc_exp_date','event_ticket','price_paid','order_price','lodging','pay_type','prereg_status','scaname','mbr_num_exp','requests','waiver1','waiver2']
df = df.drop(columns=['event_id','event_name','scaname_bad','acc_member_id','acc_exp_date','order_price','waiver1','waiver2']) # Remove unwanted columns from the import

df[['rate_age']] = df['event_ticket'].str.extract('(Child|18\+|Heirs|K\/Q)', expand=True) # Split rate, age and arival date from single field
df[['rate_mbr']] = df['event_ticket'].str.extract('(Member|Non-Member)', expand=True) # Split rate, age and arival date from single field
df[['rate_date']] = df['event_ticket'].str.extract('Arriving (\d+)', expand=True) # Split rate, age and arival date from single field

df[['mbr_num']] = df['mbr_num_exp'].str.extract('^(\d{4,})', expand=True) # Extract member number 
df['lodging'] = df['lodging'].str.extract('(.*)\s\(\$') # Remove price from camping groups


print(df.dtypes)
df.to_sql('registrations', engine, if_exists= 'append', index=False)
    

""" except:
    print("Sorry, some error has occurred!")

finally:
    engine.dispose()

 """