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

df[['rate_mbr', 'rate_age', 'rate_date']] = df['event_ticket'].str.extract('\S+\s(\S+)\s(\S+)\s\w+\s(\d+)', expand=True) # Split rate, age and arival date from single field

df[['mbr_num']] = df['mbr_num_exp'].str.extract('^(\d{4,})', expand=True) # Extract member number 
df['lodging'] = df['lodging'].str.extract('(.*)/s\(\$') # Remove price from camping groups

# Set the calculated cost
sat_price = '150' #price_df.loc[price_df['arrday'] == 'saturday', 'prereg_price'].values[0]

df['price_calc'] = '0'
df['price_calc'] = df['price_calc'].case_when([
    (df['rate_age'] != '18+' , '0'),
    ((df['rate_mbr'].str.contains('Member') & df['rate_date'].str.contains('9')) , sat_price)
    #((df['rate_mbr'].str.contains('Member') & df['rate_date'].str.contains('11')) , price_df.loc[price_df['arrday'] == 'monday', 'prereg_price'].values[0]),
    #((df['rate_mbr'].str.contains('Member') & df['rate_date'].str.contains('13')) , price_df.loc[price_df['arrday'] == 'wednesday', 'prereg_price'].values[0]),
    #((df['rate_mbr'].str.contains('Member') & df['rate_date'].str.contains('15')) , price_df.loc[price_df['arrday'] == 'friday', 'prereg_price'].values[0]) 
    ])
print (df['price_calc'])

"""if df['rate_age'] == '18+':
    if df['rate_mbr'].isin(['Member']): 
        df['price_calc'] = df['price_calc'].case_when([
            (df['rate_date'].isin(['9']) , db.select([pricing.c.prereg_price]).where(pricing.c.arrday == 'saturday')),
            (df['rate_date'].isin(['11']) , db.select([pricing.c.prereg_price]).where(pricing.c.arrday == 'monday')),
            (df['rate_date'].isin(['13']) , db.select([pricing.c.prereg_price]).where(pricing.c.arrday == 'wednesday')),
            (df['rate_date'].isin(['15']) , db.select([pricing.c.prereg_price]).where(pricing.c.arrday == 'friday'))
        ])
    else:
        df['price_calc'] = df['price_calc'].case_when([
            (df['rate_date'].isin(['9']) , db.select([pricing.c.prereg_price]).where(pricing.c.arrday == 'saturday') + db.select([pricing.c.nmr]).where(pricing.c.arrday == 'saturday')),
            (df['rate_date'].isin(['11']) , db.select([pricing.c.prereg_price]).where(pricing.c.arrday == 'monday') + db.select([pricing.c.nmr]).where(pricing.c.arrday == 'monday')),
            (df['rate_date'].isin(['13']) , db.select([pricing.c.prereg_price]).where(pricing.c.arrday == 'wednesday') + db.select([pricing.c.nmr]).where(pricing.c.arrday == 'wednesday')),
            (df['rate_date'].isin(['15']) , db.select([pricing.c.prereg_price]).where(pricing.c.arrday == 'friday') + db.select([pricing.c.nmr]).where(pricing.c.arrday == 'friday'))
        ])
else:
    df['price_calc'] = '0' """



print(df.dtypes)
df.to_sql('registrations', engine, if_exists= 'append', index=False)
    

""" except:
    print("Sorry, some error has occurred!")

finally:
    engine.dispose()

 """