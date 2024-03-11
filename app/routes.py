from app import app
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import os
import pandas as pd
from datetime import datetime
import re

price_df = pd.read_csv('gwpricing.csv')


print(price_df.dtypes)

prereg_sat_price = int(price_df.loc[price_df['arrday'] == 'saturday', 'prereg_price'].values[0])
prereg_sun_price = int(price_df.loc[price_df['arrday'] == 'sunday', 'prereg_price'].values[0])
prereg_mon_price = int(price_df.loc[price_df['arrday'] == 'monday', 'prereg_price'].values[0])
prereg_tue_price = int(price_df.loc[price_df['arrday'] == 'tuesday', 'prereg_price'].values[0])
prereg_wed_price = int(price_df.loc[price_df['arrday'] == 'wednesday', 'prereg_price'].values[0])
prereg_thur_price = int(price_df.loc[price_df['arrday'] == 'thursday', 'prereg_price'].values[0])
prereg_fri_price = int(price_df.loc[price_df['arrday'] == 'friday', 'prereg_price'].values[0])
prereg_sat2_price = int(price_df.loc[price_df['arrday'] == 'saturday2', 'prereg_price'].values[0])
door_sat_price = int(price_df.loc[price_df['arrday'] == 'saturday', 'door_price'].values[0])
door_sun_price = int(price_df.loc[price_df['arrday'] == 'sunday', 'door_price'].values[0])
door_mon_price = int(price_df.loc[price_df['arrday'] == 'monday', 'door_price'].values[0])
door_tue_price = int(price_df.loc[price_df['arrday'] == 'tuesday', 'door_price'].values[0])
door_wed_price = int(price_df.loc[price_df['arrday'] == 'wednesday', 'door_price'].values[0])
door_thur_price = int(price_df.loc[price_df['arrday'] == 'thursday', 'door_price'].values[0])
door_fri_price = int(price_df.loc[price_df['arrday'] == 'friday', 'door_price'].values[0])
door_sat2_price = int(price_df.loc[price_df['arrday'] == 'saturday2', 'door_price'].values[0])
nmr = int(price_df.loc[price_df['arrday'] == 'saturday', 'nmr'].values[0])
opening_day = str(price_df.loc[price_df['arrday'] == 'saturday', 'arrdate'].values[0])
opening_day = int(re.search("\/(\d+)\/", opening_day).group(1)) # Remove month and year so just the day is left


def get_db_connection():
    conn = psycopg2.connect(os.environ
        ###Azure Environment###
        ["AZURE_POSTGRESQL_CONNECTIONSTRING"])
        ###Local Environment###
        #host="localhost",
        #database="gwtroll-database",
        #user=os.environ["DB_USERNAME"],
        #password=os.environ["DB_PASSWORD"])


    #conn.row_factory = sqlite3.Row
    return conn

def get_reg(regid):
    conn= get_db_connection()
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM registrations WHERE regid = %s;', (regid,))
    reg = cur.fetchone()
    conn.close()
    if reg is None:
        abort(404)
    return reg

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv




""" @app.route('/')
def index():     
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM registrations order by lname, fname;')
    registrations = cur.fetchall()
    conn.close()
    for reg in registrations:
        
    return render_template('index.html', registrations=registrations) """

@app.route('/<int:regid>', methods=('GET', 'POST'))
def reg(regid):
    if request.method == 'POST':
        return redirect(url_for('checkin', regid=regid))
    else:
        reg = get_reg(regid)
    return render_template('reg.html', reg=reg)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        scaname = request.form['scaname']
        lodging = request.form['lodging']
        mbr = request.form['mbr']
        if mbr == True:
            rate_mbr = 'Member'
        else:
            rate_mbr = "Non-Member"
        age = int(request.form['age'])
        if age >= 18:
            rate_age = '18+'
        else:
            rate_age = str(age)

        if not lodging:
            flash('Lodging is required!')
        else:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            cur.execute('INSERT INTO registrations (fname, lname, scaname, lodging) VALUES (%s, %s, %s, %s);',
                         (fname, lname, scaname, lodging))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template(
        'create.html',
        lodgingdata=[{'lodging': "Open Camping"}, {'lodging': "Ansteorra - Namron"}, {'lodging': "RV"},
                    {'lodging': 'Nova'}, {'lodging': "Ansteorra - Northkeep"}])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        search_value = request.form.get('search_name')
        print(search_value)
        reg = query_db(
            "SELECT * FROM registrations WHERE fname LIKE %s OR lname LIKE %s OR scaname LIKE %s order by lname, fname",
            ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
        return render_template('index.html', searchreg=reg)
    else:
        return render_template('index.html')

@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    regid = request.args['regid']
    reg = get_reg(regid)
    price_paid = reg['price_paid']
    price_calc = reg['price_calc']


    #Calculate Total Price

    today = int(datetime.today().date().strftime('%-d'))  #Get today's day to calculate pricing
    
    if reg['rate_age'] is not None:
        if reg['rate_age'].__contains__('18+'):  #Adult Pricing
            if reg['prereg_status'] == 'SUCCEEDED':   #Pre-reg Pricing
                # Calculate daily pricing for both Members and Non-Members
                if today <= opening_day: # Saturday or Earlier
                    price_calc = prereg_sat_price
                elif  today == opening_day + 1: # Sunday
                    price_calc = prereg_sun_price 
                elif  today == opening_day + 2: # Monday 
                    price_calc = prereg_mon_price
                elif  today == opening_day + 3: # Tuesday
                    price_calc = prereg_tue_price
                elif  today == opening_day + 4: # Wednesday
                    price_calc = prereg_wed_price 
                elif  today == opening_day + 5: # Thursday
                    price_calc = prereg_thur_price
                elif  today == opening_day + 6: # Friday
                    price_calc = prereg_fri_price
                elif  today == opening_day + 7: # Saturday2
                    price_calc = prereg_sat2_price
                else:
                    print('Error, arival date out of range')
            else:  # At the Door pricing
                # Calculate daily pricing for both Members and Non-Members
                if today <= opening_day: # Saturday or Earlier
                    price_calc = door_sat_price 
                elif  today == opening_day + 1: # Sunday
                    price_calc = door_sun_price 
                elif  today == opening_day + 2: # Monday 
                    price_calc = door_mon_price
                elif  today == opening_day + 3: # Tuesday
                    price_calc = door_tue_price
                elif  today == opening_day + 4: # Wednesday
                    price_calc = door_wed_price 
                elif  today == opening_day + 5: # Thursday
                    price_calc = door_thur_price
                elif  today == opening_day + 6: # Friday
                    price_calc = door_fri_price
                elif  today == opening_day + 7: # Saturday2
                    price_calc = door_sat2_price
                else:
                    print('Error, arival date out of range')    
            if reg['rate_mbr'] == 'Non-Member':   # Add NMR to non members
                price_calc = price_calc + nmr
        else:  # Youth and Royal Pricing
            price_calc = 0
    else:  # Youth and Royal Pricing if Age Rate is None
            price_calc = 0

    #Calculate Price Due
    if price_paid > price_calc:  #Account for people who showed up late.  No refund.
        price_due = 0
    else:
        price_due = price_calc - price_paid  
    

#Check for medallion number    
    if request.method == 'POST':
        medallion = request.form['medallion']

        if not medallion:
            flash('Medallion is required!')
        else:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            #Update DB with medallion number, timestamp, and costs
            cur.execute('UPDATE registrations SET (medallion, price_calc, price_due, checkin) = (%s, %s, %s, current_timestamp(0)) WHERE regid = %s;',
                         (medallion, price_calc, price_due, regid))
            conn.commit()
            conn.close()
            return redirect(url_for('reg', regid=regid))

    return render_template('checkin.html', reg=reg, price_due=price_due, price_calc=price_calc, price_paid=price_paid)

