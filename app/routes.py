from app import app, db, login
from app.forms import CreateRegForm, CheckinForm, WaiverForm, LoginForm, EditForm, ReportForm
from app.models import Registrations, User
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory, send_file
from werkzeug.exceptions import abort
import os
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
import pandas as pd
from datetime import datetime, date
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
regcount = 0



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

def reg_count():
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT count(*) FROM registrations WHERE checkin IS NOT NULL;', [])
    results = cur.fetchone()
    for regcount in results:
        print(regcount)
    conn.close()
    if regcount is None:
        abort(404)
    return regcount

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
    regcount = reg_count()
    if request.method == "POST":
        if request.form.get('search_name'):
            search_value = request.form.get('search_name')
            print(search_value)
            reg = query_db(
                "SELECT * FROM registrations WHERE fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s order by lname, fname",
                #(search_value, search_value, search_value))
                ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
            return render_template('index.html', searchreg=reg, regcount=regcount)
        elif request.form.get('order_id'):
            search_value = request.form.get('order_id')
            print(search_value)
            reg = query_db(
                "SELECT * FROM registrations WHERE order_id = %s order by lname, fname",
                (search_value,))
            return render_template('index.html', searchreg=reg, regcount=regcount)
        elif request.form.get('medallion'):
            search_value = request.form.get('medallion')
            print(search_value)
            reg = query_db(
                "SELECT * FROM registrations WHERE medallion = %s order by lname, fname",
                (search_value,))
            return render_template('index.html', searchreg=reg, regcount=regcount)
    else:
        return render_template('index.html', regcount=regcount)
    

@app.route('/<int:regid>', methods=('GET', 'POST'))
def reg(regid):
    reg = get_reg(regid)
    if request.form.get("action") == 'Edit':
    #if request.method == 'POST' and request.path == '/editreg':
        return redirect(url_for('editreg', regid=regid))
    elif request.method == 'POST' and reg['signature'] is None:
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

@app.route('/editreg', methods=['GET', 'POST'])
def editreg():
    regid = request.args['regid']
    reg = get_reg(regid)
    kingdom = reg['kingdom']
    rate_mbr = reg['rate_mbr']
    rate_age = reg['rate_age']
    medallion = reg['medallion']
    price_due = reg['price_due']
    price_paid = reg['price_paid']
    price_calc = reg['price_calc']
    lodging = reg['lodging']
    form = EditForm(kingdom = reg['kingdom'], 
                    rate_mbr = reg['rate_mbr'], 
                    rate_age = reg['rate_age'], 
                    medallion = reg['medallion'],
                    price_due = reg['price_due'],
                    price_paid = reg['price_paid'],
                    price_calc = reg['price_calc'],
                    lodging = reg['lodging'],
                   )
    print(price_due)
    if request.method == 'POST':

        medallion = form.medallion.data
        kingdom = form.kingdom.data
        rate_mbr = form.rate_mbr.data
        rate_age = form.rate_age.data
        price_due= form.price_due.data
        price_paid = form.price_paid.data
        price_calc = form.price_calc.data
        lodging = form.lodging.data

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        #Update DB with medallion number, timestamp, and costs
        cur.execute('UPDATE registrations SET (medallion, price_calc, price_paid, price_due, rate_mbr, rate_age, kingdom, lodging) = (%s, %s, %s, %s, %s, %s, %s, %s ) WHERE regid = %s;',
                        (medallion, price_calc, price_paid, price_due, rate_mbr, rate_age, kingdom, lodging, regid))
        conn.commit()
        conn.close()
        return redirect(url_for('reg', regid=regid))

    return render_template('editreg.html', reg=reg, price_due=price_due, price_calc=price_calc, price_paid=price_paid, kingdom=kingdom, rate_mbr=rate_mbr, medallion=medallion, lodging=lodging, form=form)



@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    regid = request.args['regid']
    reg = get_reg(regid)
    #if not reg['kingdom']:
        #reg['kingdom'] = "Select Kingdom"
    form = CheckinForm(kingdom = reg['kingdom'], rate_mbr = reg['rate_mbr'], medallion = reg['medallion'], rate_age = reg['rate_age'])
    price_due= 0
    price_paid = reg['price_paid']
    price_calc = reg['price_calc']
    kingdom = reg['kingdom']
    rate_mbr = reg['rate_mbr']
    rate_age = reg['rate_age']

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
        rate_age = form.rate_age.data

        
        if rate_age is not None:
            print("Pricing Start")
            if rate_age.__contains__('18+'):  #Adult Pricing
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
                if rate_mbr == 'Non-Member':   # Add NMR to non members
                    price_calc = price_calc + nmr
            elif rate_age == 'tour_adult':
                price_calc = 20
            elif rate_age == 'tour_teen':
                price_calc = 10
            else:  # Youth and Royal Pricing
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
    form = ReportForm()
    s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
    conndict = dict(item.split("=") for item in s.split(" "))
    connstring = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
    engine=db.create_engine(connstring)
    
    file = 'test_' + str(datetime.now().isoformat(' ', 'seconds')) + '.xlsx'
    start_date = form.dt_start.data
    end_date = form.dt_end.data

   
    if form.validate_on_submit():
        report_type = form.report_type.data
        
        if report_type == 'full_export':

            file = 'full_export_' + str(datetime.now().isoformat(' ', 'seconds')) + '.csv'

            rptquery = "SELECT * FROM registrations"
            df = pd.read_sql_query(rptquery, engine)
            path1 = './reports/' + file
            path2 = '../reports/' + file
            
            df.to_csv(path1)
            
         
        if report_type == 'full_report':

            file = 'full_report_' + str(datetime.now().isoformat(' ', 'seconds')) + '.xlsx'

            rptquery = "SELECT * FROM registrations WHERE checkin::date BETWEEN {} and {}"
            rptquery = rptquery.format('%(start_date)s', '%(end_date)s')
            print(rptquery)
            params = {'start_date':start_date, 'end_date':end_date}
            df = pd.read_sql_query(rptquery, engine, params=params)
            path1 = './reports/' + file
            path2 = '../reports/' + file
            
            writer = pd.ExcelWriter(path1, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Report' ,index = False)
            worksheet = writer.sheets['Report']
            writer.close()
        
        if report_type == 'at_door_count':

            file = 'at_door_count_' + str(datetime.now().isoformat(' ', 'seconds')) + '.xlsx'

            rptquery = "SELECT count(*), sum(price_calc) FROM registrations WHERE checkin::date BETWEEN {} and {} and prereg_status is Null"
            rptquery = rptquery.format('%(start_date)s', '%(end_date)s')
            print(rptquery)
            params = {'start_date':start_date, 'end_date':end_date}
            df = pd.read_sql_query(rptquery, engine, params=params)
            rptquery = "SELECT count(*), sum(price_calc) FROM registrations WHERE checkin::date BETWEEN {} and {} and prereg_status = {}"
            rptquery = rptquery.format('%(start_date)s', '%(end_date)s', '%(prereg_status)s')
            params = {'start_date':start_date, 'end_date':end_date, 'prereg_status':"SUCCEEDED"}
            df = df.merge(pd.read_sql_query(rptquery, engine, params=params), how='outer')

            path1 = './reports/' + file
            path2 = '../reports/' + file

            writer = pd.ExcelWriter(path1, engine='xlsxwriter')

            df.to_excel(writer, sheet_name='Report' ,index = False, startcol=1)
            workbook = writer.book
            worksheet = writer.sheets["Report"]           
            worksheet.write('A2', "At the Door")
            worksheet.write('A3', "Pre-Reg")
            worksheet.write('C1', "Income Total")

            writer.close()
        
        if report_type == 'kingdom_count':

            file = 'kingdom_count_' + str(datetime.now().isoformat(' ', 'seconds')) + '.xlsx'

            rptquery = "SELECT kingdom, count(*) FROM registrations WHERE checkin::date BETWEEN {} and {} GROUP BY kingdom, checkin::date ORDER BY kingdom"
            rptquery = rptquery.format('%(start_date)s', '%(end_date)s')
            print(rptquery)
            params = {'start_date':start_date, 'end_date':end_date}
            df = pd.read_sql_query(rptquery, engine, params=params)
            
            path1 = './reports/' + file
            path2 = '../reports/' + file

            writer = pd.ExcelWriter(path1, engine='xlsxwriter')

            df.to_excel(writer, sheet_name='Report' ,index = False)
            workbook = writer.book
            worksheet = writer.sheets["Report"]

            writer.close()

        if report_type == 'ghost_report':

            file = 'ghost_report_' + str(datetime.now().isoformat(' ', 'seconds')) + '.xlsx'

            rptquery = "SELECT * FROM registrations WHERE prereg_status = {} AND checkin IS NULL"
            rptquery = rptquery.format('%(prereg_status)s')
            print(rptquery)
            params = {'prereg_status':"SUCCEEDED"}
            df = pd.read_sql_query(rptquery, engine, params=params)
            path1 = './reports/' + file
            path2 = '../reports/' + file

            writer = pd.ExcelWriter(path1, engine='xlsxwriter')
            #worksheet = writer.sheets['Report']

            df.to_excel(writer, sheet_name='Report' ,index = False)
            writer.close()

        return send_file(path2)
    return render_template('reports.html', form=form)

    
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