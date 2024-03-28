from app import app, db, login
from app.forms import CreateRegForm, CheckinForm, WaiverForm, LoginForm, EditForm, ReportForm, EditUserForm, UpdatePasswordForm, CreateUserForm
from app.models import Registrations, User, Role, UserRoles
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory, send_file
from werkzeug.exceptions import abort
import os
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
import sqlalchemy as sa
import pandas as pd
from datetime import datetime, date
import re
from urllib.parse import urlsplit
from markupsafe import Markup

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
    reg = Registrations.query.filter_by(regid=regid).first()
    if reg is None:
        abort(404)
    return reg

def get_user(userid):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        abort(404)
    return user

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
    elif request.method == 'POST' and reg.signature is None:
        return redirect(url_for('waiver', regid=regid))
    elif request.method == 'POST':
        return redirect(url_for('checkin', regid=regid))
    else:
        return render_template('reg.html', reg=reg)

@app.route('/users', methods=('GET', 'POST'))
def users():
    users = query_db("SELECT * FROM public.users")
    return render_template('users.html', users=users)


@app.route('/user/create', methods=('GET', 'POST'))
def createuser():

    form = CreateUserForm()
    
    if request.method == 'POST':
        user = User()
        user.username = form.username.data
        user.role = form.role.data
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        db.session.close()

        return redirect('/users')

    return render_template('createuser.html', form=form)

@app.route('/user', methods=('GET', 'POST'))
def edituser():
    user = get_user(request.args.get("userid"))
    edit_request = request.args.get("submitValue")
    print(edit_request)
    if edit_request == "Edit" :
        form = EditUserForm(
            id = user.id, 
            username = user.username, 
            role = user.role, 
            fname = user.fname,
            lname = user.lname,
        )
        
    elif edit_request == "Password Reset":
        form = UpdatePasswordForm(
            id = user.id, 
            username = user.username, 
            password = ''
        )

    if request.method == 'POST' and edit_request == 'Edit':
        user = get_user(form.id.data)
        user.username = form.username.data
        user.role = form.role.data
        user.fname = form.fname.data
        user.lname = form.lname.data

        db.session.commit()
        db.session.close()

        return redirect('/users')

    if request.method == 'POST'  and edit_request == 'Password Reset':
        user = get_user(form.id.data)
        user.set_password(form.password.data)

        db.session.commit()
        db.session.close()

        return redirect('/users')
    
    return render_template('edituser.html', user=user, form=form, edit_request=edit_request)

@app.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':   
        f = request.files['file'] 
        f.save(f.filename)
        print(os.path.join(os.path.abspath(os.path.dirname(app.root_path)),"../",f.filename))

        s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
        conndict = dict(item.split("=") for item in s.split(" "))
        connstring = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
        engine=db.create_engine(connstring)
        metadata = db.MetaData()
        registrations = db.Table('registrations', metadata)

        root_path = os.path.dirname(os.path.dirname( __file__ ))
        df = pd.read_csv(os.path.join(root_path,f.filename))


        # Rename columns from CSV to match DB - order is important
        df.columns = ['event_id','event_name','order_id','reg_date_time','medallion','fname','lname','scaname_bad','acc_member_id','acc_exp_date','event_ticket','price_paid','order_price','lodging','pay_type','prereg_status','kingdom','regid','scaname','mbr_num_exp','requests','waiver1','waiver2']
        df = df.drop(columns=['event_id','event_name','scaname_bad','acc_member_id','acc_exp_date','order_price','waiver1','waiver2']) # Remove unwanted columns from the import

        df[['rate_age']] = df['event_ticket'].str.extract('(Child|18\+|Heirs|K\/Q|Royals)', expand=True) # Split rate, age and arival date from single field
        df[['rate_mbr']] = df['event_ticket'].str.extract('(Member|Non-Member)', expand=True) # Split rate, age and arival date from single field
        df[['rate_date']] = df['event_ticket'].str.extract('Arriving (\d+)', expand=True) # Split rate, age and arival date from single field

        df[['mbr_num']] = df['mbr_num_exp'].str.extract('^(\d{4,})', expand=True) # Extract member number 
        df['lodging'] = df['lodging'].str.extract('(.*)\s\(\$') # Remove price from camping groups


        # Import data to DB
        df.to_sql('registrations', engine, if_exists= 'append', index=False)

        # Adjust regid for at-the-door registrations
        conn = psycopg2.connect(os.environ["AZURE_POSTGRESQL_CONNECTIONSTRING"])
        cur = conn.cursor()
        cur.execute ('ALTER SEQUENCE registrations_regid_seq RESTART WITH 60001;')
        conn.commit()
        conn.close()
        flash("SUCCESS!")
    return render_template('upload.html')

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

        regid = reg.regid
        flash('Registration {} created for {} {}.'.format(
            reg.regid, reg.fname, reg.lname))

        return redirect(url_for('reg', regid=regid))
    return render_template('create.html', title = 'New Registration', form=form)

@app.route('/editreg', methods=['GET', 'POST'])
def editreg():
    regid = request.args['regid']
    reg = get_reg(regid)

    form = EditForm(
        kingdom = reg.kingdom, 
        rate_mbr = reg.rate_mbr, 
        rate_age = reg.rate_age, 
        medallion = reg.medallion,
        price_due = reg.price_due,
        price_paid = reg.price_paid,
        price_calc = reg.price_calc,
        lodging = reg.lodging,
        )

    if request.method == 'POST':

        medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()

        if medallion_check is not None and int(regid) != int(medallion_check.regid):
            flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.regid) )
            dup_url = '<a href=' + url_for('reg', regid=str(medallion_check.regid)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
            flash(Markup(dup_url))

        else:

            reg.medallion = form.medallion.data
            reg.kingdom = form.kingdom.data
            reg.rate_mbr = form.rate_mbr.data
            reg.rate_age = form.rate_age.data
            reg.price_due= form.price_due.data
            reg.price_paid = form.price_paid.data
            reg.price_calc = form.price_calc.data
            reg.lodging = form.lodging.data

            db.session.commit()
            db.session.close()
            return render_template('/<int:regid>', regid=regid)

    return render_template('editreg.html', regid=reg.regid, reg=reg, form=form)



@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    regid = request.args['regid']
    reg = get_reg(regid)

    form = CheckinForm(kingdom = reg.kingdom, rate_mbr = reg.rate_mbr, medallion = reg.medallion, rate_age = reg.rate_age)
    price_due = 0
    price_paid = reg.price_paid
    price_calc = reg.price_calc
    kingdom = reg.kingdom
    rate_mbr = reg.rate_mbr
    rate_age = reg.rate_age

    print(form.kingdom)

    #if form.validate_on_submit():
        #print(form)
    #Calculate Total Price

    #today = int(datetime.today().date().strftime('%-d'))  #Get today's day to calculate pricing
    
    today = date.today().day

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
                if reg.prereg_status == 'SUCCEEDED':   #Pre-reg Pricing
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
    
            
        medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()

        if medallion_check is not None and int(regid) != int(medallion_check.regid):
            flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.regid) )
            dup_url = '<a href=' + url_for('reg', regid=str(medallion_check.regid)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
            flash(Markup(dup_url))
        else:

            reg.medallion = medallion
            reg.price_calc = price_calc
            reg.price_due = price_due
            reg.rate_mbr = rate_mbr
            reg.kingdom = kingdom

            db.session.commit()
            db.session.close()

            return redirect(url_for('reg', regid=regid))

    return render_template('checkin.html', reg=reg, form=form)

@app.route('/full_signature_export', methods=('GET', 'POST'))
def full_export():
    regs = query_db("SELECT * FROM registrations WHERE signature IS NOT NULL")
    return render_template('full_export_images.html', regs=regs)

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    form = ReportForm()
    s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
    conndict = dict(item.split("=") for item in s.split(" "))
    connstring = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
    engine=db.create_engine(connstring)
    
    file = 'test_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_")) + '.xlsx'
    start_date = form.dt_start.data
    end_date = form.dt_end.data
   
    if form.validate_on_submit():
        report_type = form.report_type.data

        if report_type == 'full_signatue_export':
            regs = query_db("SELECT * FROM registrations WHERE signature IS NOT NULL")
            return render_template('full_export_images.html', regs=regs)
        
        if report_type == 'full_export':

            file = 'full_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

            rptquery = "SELECT * FROM registrations"
            df = pd.read_sql_query(rptquery, engine)
            path1 = './reports/' + file
            path2 = '../reports/' + file
            
            writer = pd.ExcelWriter(path1, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Report' ,index = False)
            worksheet = writer.sheets['Report']
            writer.close()
            
         
        if report_type == 'full_checkin_report':

            file = 'full_checkin_report_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

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

            file = 'at_door_count_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

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

            file = 'kingdom_count_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

            date_check = query_db(
            "SELECT DISTINCT checkin::DATE FROM registrations WHERE checkin IS NOT NULL;")

            date_cols = []
            for d  in date_check:
                date_cols.append("\"" + str(d['checkin']) + "\" bigint")
            date_cols_str =', '.join(date_cols)

            rptquery = "CREATE EXTENSION IF NOT EXISTS tablefunc; SELECT * FROM crosstab('SELECT kingdom, checkin::DATE, COUNT(regid) FROM registrations WHERE checkin::date IS NOT NULL GROUP BY kingdom, checkin::date ORDER BY 1', 'SELECT DISTINCT checkin::DATE FROM registrations WHERE checkin IS NOT NULL;') AS (kingdom text, "+ date_cols_str +");"

            df = pd.read_sql_query(rptquery, engine)
            
            path1 = './reports/' + file
            path2 = '../reports/' + file

            writer = pd.ExcelWriter(path1, engine='xlsxwriter')

            df.to_excel(writer, sheet_name='Report' ,index = False)
            workbook = writer.book
            worksheet = writer.sheets["Report"]

            writer.close()

        if report_type == 'ghost_report':

            file = 'ghost_report_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

            rptquery = "SELECT order_id, regid, fname, lname, scaname, rate_age, lodging, prereg_status, checkin FROM registrations WHERE prereg_status = {} AND checkin IS NULL ORDER BY lodging"
            rptquery = rptquery.format('%(prereg_status)s')
            print(rptquery)
            params = {'prereg_status':"SUCCEEDED"}
            df = pd.read_sql_query(rptquery, engine, params=params)
            path1 = './reports/' + file
            path2 = '../reports/' + file

            writer = pd.ExcelWriter(path1, engine='xlsxwriter')

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

        reg.signature = form.signature.data
        db.session.commit()

        return redirect(url_for('reg', regid=regid))

    return render_template('waiver.html', form=form)