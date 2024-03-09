from app import app, db, login
from app.forms import CreateRegForm, CheckinForm, WaiverForm
from app.models import Registrations, User
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import os
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
import pandas as pd
from datetime import datetime
import re
from urllib.parse import urlsplit

#Import pricing from CSV and set global variables
price_df = pd.read_csv('gwpricing.csv')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        if request.form.get('search_name'):
            search_value = request.form.get('search_name')
            print(search_value)
            reg = query_db(
                "SELECT * FROM registrations WHERE fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s order by lname, fname",
                #(search_value, search_value, search_value))
                ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
            return render_template('index.html', searchreg=reg)
        elif request.form.get('order_id'):
            search_value = request.form.get('order_id')
            print(search_value)
            reg = query_db(
                "SELECT * FROM registrations WHERE order_id = %s order by lname, fname",
                (search_value,))
            return render_template('index.html', searchreg=reg)
    else:
        return render_template('index.html')
    

@app.route('/<int:regid>', methods=('GET', 'POST'))
def reg(regid):
    reg = get_reg(regid)
    if request.method == 'POST' and reg['signature'] is None:
        return redirect(url_for('waiver', regid=regid))
    elif request.method == 'POST':
        return redirect(url_for('checkin', regid=regid))
    else:
        return render_template('reg.html', reg=reg)

@app.route('/create', methods=('GET', 'POST'))
def create():
    form = CreateRegForm()
    if form.validate_on_submit():

        reg = Registrations(
        fname = form.fname.data,
        lname = form.lname.data,
        scaname = form.scaname.data,
        kingdom = form.kingdom.data,
        lodging = form.lodging.data,
        rate_age = form.rate_age.data,
        rate_mbr = form.rate_mbr.data,
        price_paid = 0)
        #mbr_num = form.mbr_num.data,
        #mbr_exp = form.mbr_exp.data)

        db.session.add(reg)
        db.session.commit()
        print(reg.regid)
        regid = reg.regid
        flash('Registration {} created for {} {}.'.format(
            regid, reg.fname, reg.lname))

        return redirect(url_for('reg', regid=regid))
    return render_template('create.html', title = 'New Registration', form=form)


@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    regid = request.args['regid']
    reg = get_reg(regid)
    #if not reg['kingdom']:
        #reg['kingdom'] = "Select Kingdom"
    form = CheckinForm(kingdom = reg['kingdom'], rate_mbr = reg['rate_mbr'], medallion = reg['medallion'])
    price_due= 0
    price_paid = reg['price_paid']
    price_calc = reg['price_calc']
    kingdom = reg['kingdom']
    rate_mbr = reg['rate_mbr']

    print(form.kingdom)

    #if form.validate_on_submit():
        #print(form)
    #Calculate Total Price

    today = int(datetime.today().date().strftime('%-d'))  #Get today's day to calculate pricing
    
    if today >= 23:
        today = 9
    
    print(today)

    
    

    #Check for medallion number    
    if request.method == 'POST':
        medallion = form.medallion.data
        kingdom = form.kingdom.data
        rate_mbr = form.rate_mbr.data

        if not medallion:
            flash('Medallion is required!')
            flash('form.kingdom.data')       
        elif reg['rate_age'] is not None:
            print("Pricing Start")
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
            print("Calculating price:", price_calc) 
    
            
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        #Update DB with medallion number, timestamp, and costs
        cur.execute('UPDATE registrations SET (medallion, price_calc, price_due, rate_mbr, kingdom, checkin) = (%s, %s, %s, %s, %s, current_timestamp(0)) WHERE regid = %s;',
                        (medallion, price_calc, price_due, rate_mbr, kingdom, regid))
        conn.commit()
        conn.close()
        return redirect(url_for('reg', regid=regid))

    return render_template('checkin.html', reg=reg, price_due=price_due, price_calc=price_calc, price_paid=price_paid, kingdom=kingdom, rate_mbr=rate_mbr, form=form)

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    
    if request.method == "POST":
        if request.form.get('search_name'):
            search_value = request.form.get('search_name')
            print(search_value)
            reg = query_db(
                "SELECT * FROM registrations WHERE fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s order by lname, fname",
                #(search_value, search_value, search_value))
                ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
            return render_template('index.html', searchreg=reg)
        elif request.form.get('order_id'):
            search_value = request.form.get('order_id')
            print(search_value)
            reg = query_db(
                "SELECT * FROM registrations WHERE order_id = %s order by lname, fname",
                (search_value,))
            return render_template('index.html', searchreg=reg)
    else:
        return render_template('reports.html')
    
@app.route('/waiver', methods=['GET', 'POST'])
def waiver():
    form = WaiverForm()
    regid = request.args['regid']
    reg = get_reg(regid)
    if request.method == 'POST':
        signature = form.signature.data
        print(signature)
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        #Update DB with medallion number, timestamp, and costs
        cur.execute('UPDATE registrations SET signature = %s WHERE regid = %s;',(signature, regid))

        conn.commit()
        conn.close()
        return redirect(url_for('reg', regid=regid))

    return render_template('waiver.html', form=form)