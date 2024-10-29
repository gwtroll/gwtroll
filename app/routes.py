from app import app, db, login
from app.forms import *
from app.models import Registrations, User, Role, UserRoles, RegLogs
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory, send_file
from werkzeug.exceptions import abort
import os
from flask_login import current_user, login_user, logout_user, login_required
from flask_security import roles_accepted
from werkzeug.security import generate_password_hash
import sqlalchemy as sa
from sqlalchemy import and_, or_
import pandas as pd
from datetime import datetime, date
import re
from urllib.parse import urlsplit
from markupsafe import Markup
import uuid
import json

@login.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

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

def get_reg_by_invoice(invoice_number):
    reg = Registrations.query.filter(Registrations.invoice_number == invoice_number).first()
    if reg is None:
        abort(404)
    return reg

def is_duplicate_invoice_number(invoice_number, reg):
    new_reg = Registrations.query.filter(and_(Registrations.invoice_number == invoice_number, Registrations.regid != reg.regid, Registrations.email != reg.email)).first()
    if new_reg is None:
        return False
    else:
        return True

def get_roles():
    roles = Role.query.all()
    role_return = []
    [role_return.append((role.id,role.name)) for role in roles]
    return role_return

def get_user(userid):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        abort(404)
    return user

def get_user_roles(userid):
    userRoles = UserRoles.query.filter_by(user_id=userid).first()
    if userRoles is None:
        abort(404)
    return userRoles

def get_role(roleid):
    role = Role.query.filter_by(id=roleid).first()
    if role is None:
        abort(404)
    return role

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

def calculate_price_calc(reg):
    today_datetime = date.today()
    if today_datetime < datetime(2025,3,8).date():
        today_date = datetime(2025,3,8).strftime('%m-%d-%Y')
    elif today_datetime > datetime(2025,3,15).date():
        today_date = datetime(2025,3,15).strftime('%m-%d-%Y')
    else:
        today_date = today_datetime.strftime('%m-%d-%Y')

    with open('rate_sheet.json') as f:
        rate_sheet = json.load(f)
        if reg.rate_age.__contains__('18+'):
            if reg.prereg_status == 'SUCCEEDED' and reg.rate_mbr == 'Member':
                price_calc = rate_sheet['Pre-Registered Member'][today_date]
            elif reg.prereg_status != 'SUCCEEDED' and reg.rate_mbr == 'Member':
                price_calc = rate_sheet['At the Door Member'][today_date]
            elif reg.prereg_status == 'SUCCEEDED' and reg.rate_mbr != 'Member':
                price_calc = rate_sheet['Pre-Registered Non-Member'][today_date]
            elif reg.prereg_status != 'SUCCEEDED' and reg.rate_mbr != 'Member':
                price_calc = rate_sheet['At the Door Non-Member'][today_date]               
        else:
            price_calc = 0

    return price_calc

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def log_reg_action(reg, action):
    print(reg)
    reglog = RegLogs(
        regid = reg.regid,
        userid = current_user.id,
        timestamp = datetime.now(),
        action = action
    )
    db.session.add(reglog)
    db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data) or not user.active:
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
@login_required
def index():
    regcount = reg_count()
    if request.method == "POST":
        if request.form.get('search_name'):
            search_value = request.form.get('search_name')
            print('bob')
            print(search_value)
            if search_value is not None and search_value != '':
                reg = query_db(
                    "SELECT * FROM registrations WHERE fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s order by lname, fname",
                    #(search_value, search_value, search_value))
                    ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
            return render_template('index.html', searchreg=reg, regcount=regcount)
        elif request.form.get('order_id'):
            search_value = request.form.get('order_id')
            reg = query_db(
                "SELECT * FROM registrations WHERE order_id = %s order by lname, fname",
                (search_value,))
            return render_template('index.html', searchreg=reg, regcount=regcount)
        elif request.form.get('medallion'):
            search_value = request.form.get('medallion')
            reg = query_db(
                "SELECT * FROM registrations WHERE medallion = %s order by lname, fname",
                (search_value,))
            return render_template('index.html', searchreg=reg, regcount=regcount)
    else:
        return render_template('index.html', regcount=regcount)

@app.route('/<int:regid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Troll Shift Lead','Troll User','Cashier')
def reg(regid):
    reg = get_reg(regid)
    if request.form.get("action") == 'Edit':
    #if request.method == 'POST' and request.path == '/editreg':
        return redirect(url_for('editreg', regid=regid))
    elif request.method == 'POST' and reg.signature is None and request.form.get("action") == 'waiver':
        return redirect(url_for('waiver', regid=regid))
    elif request.method == 'POST' and request.form.get("action") == 'payment':
        return redirect(url_for('payment', regid=regid))
    elif request.method == 'POST'and request.form.get("action") == 'checkin':
        return redirect(url_for('checkin', regid=regid))
    else:
        return render_template('reg.html', reg=reg)
    
@app.route('/invoice/unsent', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices')
def unsentinvoices():
    regs = Registrations.query.filter(and_(Registrations.invoice_number == None, Registrations.invoice_date == None, Registrations.prereg_status == "SUCCEEDED")).all()
    return render_template('invoice_list.html', regs=regs, back='unsent')

@app.route('/invoice/open', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices')
def openinvoices():
    regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.invoice_date != None, Registrations.prereg_status == "SUCCEEDED", Registrations.invoice_status == 'SENT')).all()
    return render_template('invoice_list.html', regs=regs, back='open')

@app.route('/invoice/paid', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices')
def paidinvoices():
    regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.invoice_date != None, Registrations.prereg_status == "SUCCEEDED", Registrations.invoice_status == 'PAID')).all()
    return render_template('invoice_list.html', regs=regs, back='paid')

@app.route('/invoice/canceled', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices')
def canceledinvoices():
    regs = Registrations.query.filter(and_(Registrations.prereg_status == "SUCCEEDED", Registrations.invoice_status == 'CANCELED')).all()
    return render_template('invoice_list.html', regs=regs, back='canceled')

@app.route('/invoice/<int:regid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices')
def updateinvoice(regid):
    back = request.args.get('back')
    reg = get_reg(regid)
    form = UpdateInvoiceForm()
    form.price_paid.data = reg.price_paid
    form.price_calc.data = reg.price_calc
    form.paypal_donation_amount.data = reg.paypal_donation_amount
    form.price_due.data = reg.price_due
    form.invoice_number.data = reg.invoice_number
    form.invoice_paid.data = reg.invoice_paid
    if reg.invoice_date is not None:
        form.invoice_date.data = reg.invoice_date
    else:
        form.invoice_date.data = datetime.now()
    form.invoice_canceled.data = reg.invoice_canceled
    form.invoice_payment_date.data = reg.invoice_payment_date
    
    if request.method == 'POST':
        invoice_number = request.form.get('invoice_number')
        price_paid = int(request.form.get('price_paid'))
        price_calc = int(request.form.get('price_calc'))
        invoice_date = request.form.get('invoice_date')
        invoice_payment_date = request.form.get('invoice_payment_date')
        invoice_canceled = bool(request.form.get('invoice_canceled'))

        if is_duplicate_invoice_number(invoice_number, reg):
            flash('Duplicate Invoice Number {}'.format(
            invoice_number))
            return render_template('update_invoice.html', reg=reg, form=form)
        
        if invoice_number is not None and invoice_number != '':
            reg.invoice_status = 'SENT'
        if int(price_paid) >= int(price_calc) + int(reg.paypal_donation_amount):
            reg.invoice_status = 'PAID'
        if bool(request.form.get('invoice_canceled')) == True:
            reg.invoice_status = 'CANCELED'

        reg.price_paid = price_paid
        reg.price_calc = price_calc
        if invoice_number != None and invoice_number != '':          
            reg.invoice_number = invoice_number

        if invoice_date != '' and invoice_date is not None:
            reg.invoice_date = invoice_date
        if invoice_payment_date != '' and invoice_payment_date is not None:
            reg.invoice_payment_date = invoice_payment_date

        reg.invoice_canceled = invoice_canceled

        reg.price_due = (price_calc + reg.paypal_donation_amount) - price_paid

        reg.pay_type = 'paypal'

        db.session.commit()

        log_reg_action(reg, 'INVOICE UPDATED')

        match back:
            case 'unsent': 
                return redirect('/invoice/unsent')
            case 'open': 
                return redirect('/invoice/open')
            case 'paid': 
                return redirect('/invoice/paid')
            case 'canceled': 
                return redirect('/invoice/canceled')
            case _:
                return redirect('/')


    return render_template('update_invoice.html', reg=reg, form=form)


@app.route('/users', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/user/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def createuser():

    form = CreateUserForm()
    form.role.choices = get_roles()
    
    if request.method == 'POST':
        user = User()
        user.username = form.username.data
        for roleid in form.role.data:
            user.roles.append(get_role(roleid))
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.fs_uniquifier = uuid.uuid4().hex
        user.active = True
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        db.session.close()

        return redirect('/users')

    return render_template('createuser.html', form=form)

@app.route('/user', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def edituser():
    user = get_user(request.args.get("userid"))
    edit_request = request.args.get("submitValue")
    if edit_request == "Edit" :
        role_array = []
        for role in user.roles:
            role_array.append(role.id)
        form = EditUserForm(
            id = user.id, 
            username = user.username, 
            role = role_array,
            fname = user.fname,
            lname = user.lname,
            active = user.active
        )
        form.role.choices = get_roles()
        
    elif edit_request == "Password Reset":
        form = UpdatePasswordForm(
            id = user.id, 
            username = user.username, 
            password = ''
        )

    if request.method == 'POST' and edit_request == 'Edit':
        role_array = []
        for roleid in form.role.data:
            role_array.append(get_role(roleid))
        user = get_user(form.id.data)
        user.username = form.username.data
        user.roles = role_array
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.active = request.form.get('active')

        db.session.commit()

        return redirect('/users')

    if request.method == 'POST'  and edit_request == 'Password Reset':
        user = get_user(form.id.data)
        user.set_password(form.password.data)

        db.session.commit()

        return redirect('/users')
    
    return render_template('edituser.html', user=user, form=form, edit_request=edit_request)

@app.route('/upload', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def upload():
    if request.method == 'POST':   
        f = request.files['file'] 
        f.save(f.filename)

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

@app.route('/registration', methods=('GET', 'POST'))
def createprereg():
    form = CreatePreRegForm()
    if form.validate_on_submit() and request.method == 'POST':
        reg = Registrations(
            fname = form.fname.data,
            lname = form.lname.data,
            scaname = form.scaname.data,
            city = form.city.data,
            state_province = form.state_province.data,
            zip = form.zip.data,
            country = form.country.data,
            phone = form.phone.data, 
            email = form.email.data, 
            invoice_email = form.invoice_email.data,
            rate_age = form.rate_age.data,
            kingdom = form.kingdom.data, 
            lodging = form.lodging.data, 
            prereg_status = 'SUCCEEDED',
            invoice_status = 'UNSENT',
            rate_mbr = form.rate_mbr.data,
            mbr_num_exp = form.mbr_num_exp.data, 
            mbr_num = form.mbr_num.data,
            onsite_contact_name = form.onsite_contact_name.data, 
            onsite_contact_sca_name = form.onsite_contact_sca_name.data, 
            onsite_contact_kingdom = form.onsite_contact_kingdom.data, 
            onsite_contact_group = form.onsite_contact_group.data, 
            offsite_contact_name = form.offsite_contact_name.data, 
            offsite_contact_phone = form.offsite_contact_phone.data,
            prereg_date_time = datetime.now().replace(microsecond=0).isoformat(),
            paypal_donation = form.paypal_donation.data,
            price_paid = 0,
            atd_paid = 0,
        )

        print(form.rate_date.data)
        if form.rate_date.data == 'Early_On':
            reg.early_on = True
            rate_date = '03-08-2025'
            reg.rate_date = datetime.strptime('03-08-2025', '%m-%d-%Y'),
        else:
            rate_date = form.rate_date.data
            reg.rate_date = datetime.strptime(form.rate_date.data, '%m-%d-%Y'),

        if form.rate_age.data != '18+':
            rate_category = 'CHILDREN 17 AND UNDER'
        elif form.rate_mbr.data == 'Member':
            rate_category = 'Pre-Registered Member'
        elif form.rate_mbr.data == 'Non-Member':
            rate_category = 'Pre-Registered Non-Member'

        with open('rate_sheet.json') as f:
            rate_sheet = json.load(f)
            reg.price_calc = rate_sheet[rate_category][rate_date]
            reg.price_due = rate_sheet[rate_category][rate_date]

        if reg.paypal_donation == True:
            reg.paypal_donation_amount = 3
        else:
            reg.paypal_donation_amount = 0

        reg.price_due += reg.paypal_donation_amount

        print(reg.early_on)
        db.session.add(reg)
        db.session.commit()

        regid = reg.regid
        flash('Registration {} created for {} {}.'.format(
            reg.regid, reg.fname, reg.lname))
        
        return redirect(url_for('success'))
    return render_template('create_prereg.html', titl='New Registration', form=form)

@app.route('/success')
def success():
    return render_template('reg_success.html')


@app.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Troll Shift Lead','Troll User')
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
        onsite_contact_name = form.onsite_contact_name.data, 
        onsite_contact_sca_name = form.onsite_contact_sca_name.data, 
        onsite_contact_kingdom = form.onsite_contact_kingdom.data, 
        onsite_contact_group = form.onsite_contact_group.data, 
        offsite_contact_name = form.offsite_contact_name.data, 
        offsite_contact_phone = form.offsite_contact_phone.data,
        atd_paid = 0,
        price_paid = 0)
        #mbr_num = form.mbr_num.data,
        #mbr_exp = form.mbr_exp.data)
        reg.price_calc = calculate_price_calc(reg)
        if reg.price_paid + reg.atd_paid > reg.price_calc:  #Account for people who showed up late.  No refund.
            reg.price_due = 0
        else:
            reg.price_due = reg.price_calc - (reg.price_paid + reg.atd_paid)

        db.session.add(reg)
        db.session.commit()

        log_reg_action(reg, 'CREATE')

        regid = reg.regid
        flash('Registration {} created for {} {}.'.format(
            reg.regid, reg.fname, reg.lname))

        return redirect(url_for('reg', regid=regid))
    return render_template('create.html', title = 'New Registration', form=form)

@app.route('/editreg', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', 'Troll Shift Lead')
def editreg():
    regid = request.args['regid']
    reg = get_reg(regid)

    form = EditForm(
        regid = reg.regid,
        fname = reg.fname,
        lname = reg.lname,
        scaname = reg.scaname,
        city = reg.city,
        state_province = reg.state_province,
        zip = reg.zip,
        country = reg.country,
        phone = reg.phone,
        email = reg.email,
        invoice_email = reg.invoice_email,
        kingdom = reg.kingdom,
        lodging = reg.lodging,
        rate_age = reg.rate_age,
        rate_mbr = reg.rate_mbr,
        medallion = reg.medallion,
        atd_paid = reg.atd_paid,
        price_paid = reg.price_paid,
        pay_type = reg.atd_pay_type,
        price_calc = reg.price_calc,
        price_due = reg.price_due,
        paypal_donation = reg.paypal_donation,
        paypal_donation_amount = reg.paypal_donation_amount,
        prereg_status = reg.prereg_status,
        early_on =reg.early_on,
        mbr_num = reg.mbr_num,
        mbr_num_exp = reg.mbr_num_exp,
        onsite_contact_name = reg.onsite_contact_name,
        onsite_contact_sca_name = reg.onsite_contact_sca_name,
        onsite_contact_kingdom = reg.onsite_contact_kingdom,
        onsite_contact_group = reg.onsite_contact_group,
        offsite_contact_name = reg.offsite_contact_name,
        offsite_contact_phone = reg.offsite_contact_phone
    )

    if request.method == 'POST':

        medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()

        if medallion_check is not None and int(regid) != int(medallion_check.regid):
            flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.regid) )
            dup_url = '<a href=' + url_for('reg', regid=str(medallion_check.regid)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
            flash(Markup(dup_url))

        else:
            reg.fname = request.form.get('fname')
            reg.lname = request.form.get('lname')
            reg.scaname = request.form.get('scaname')
            reg.city = request.form.get('city')
            reg.state_province = request.form.get('state_province')
            if request.form.get('zip'):
                reg.zip = int(request.form.get('zip'))
            else: reg.zip = None
            reg.country = request.form.get('country')
            reg.phone = request.form.get('phone')
            reg.email = request.form.get('email')
            reg.invoice_email = request.form.get('invoice_email')
            reg.kingdom = request.form.get('kingdom')
            reg.lodging = request.form.get('lodging')
            reg.rate_age = request.form.get('rate_age')
            reg.rate_mbr = request.form.get('rate_mbr')
            if request.form.get('medallion'):
                reg.medallion = int(request.form.get('medallion'))
            else: reg.medallion = None
            if request.form.get('atd_paid'):
                reg.atd_paid = int(request.form.get('atd_paid'))
            else: reg.atd_paid = 0
            if request.form.get('price_paid'):
                reg.price_paid = int(request.form.get('price_paid'))
            else: reg.price_paid =  0
            if request.form.get('pay_type') == '' or request.form.get('pay_type') == None:
                reg.atd_pay_type = None
            else: reg.atd_pay_type = request.form.get('pay_type')
            if request.form.get('price_calc'):
                reg.price_calc = int(request.form.get('price_calc'))
            else: reg.price_calc = 0
            if request.form.get('price_due'):
                reg.price_due = int(request.form.get('price_due'))
            else: reg.price_due = 0
            reg.paypal_donation = bool(request.form.get('paypal_donation'))
            if request.form.get('paypal_donation_amount'):
                reg.paypal_donation_amount = int(request.form.get('paypal_donation_amount'))
            else: reg.paypal_donation_amount = 0
            reg.prereg_status = request.form.get('prereg_status')
            reg.early_on = bool(request.form.get('early_on'))
            if request.form.get('mbr_num'):
                reg.mbr_num = int(request.form.get('mbr_num'))
            else: reg.mbr_num = None
            reg.mbr_num_exp = request.form.get('mbr_num_exp')
            reg.onsite_contact_name = request.form.get('onsite_contact_name')
            reg.onsite_contact_sca_name = request.form.get('onsite_contact_sca_name')
            reg.onsite_contact_kingdom = request.form.get('onsite_contact_kingdom')
            reg.onsite_contact_group = request.form.get('onsite_contact_group')
            reg.offsite_contact_name = request.form.get('offsite_contact_name')
            reg.offsite_contact_phone = request.form.get('offsite_contact_phone') 

            reg.price_due = (reg.price_calc + reg.paypal_donation_amount) - (reg.price_paid + reg.atd_paid)
            if reg.price_due < 0:  #Account for people who showed up late.  No refund.
                reg.price_due = 0

            db.session.commit()

            log_reg_action(reg, 'EDIT')

            return redirect(url_for('reg',regid=regid))

    return render_template('editreg.html', regid=reg.regid, reg=reg, form=form)



@app.route('/checkin', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin','Troll Shift Lead','Troll User')
def checkin():
    regid = request.args['regid']
    reg = get_reg(regid)

    form = CheckinForm(kingdom = reg.kingdom, rate_mbr = reg.rate_mbr, medallion = reg.medallion, rate_age = reg.rate_age)
    price_paid = reg.price_paid
    price_calc = reg.price_calc
    kingdom = reg.kingdom
    rate_mbr = reg.rate_mbr
    rate_age = reg.rate_age

    #if form.validate_on_submit():
        #print(form)
    #Calculate Total Price

    #today = int(datetime.today().date().strftime('%-d'))  #Get today's day to calculate pricing

    #Check for medallion number    
    if request.method == 'POST':
        medallion = form.medallion.data
        kingdom = form.kingdom.data
        rate_mbr = form.rate_mbr.data
        rate_age = form.rate_age.data
        
        # if rate_age is not None:
        #     print("Pricing Start")
        #     if rate_age.__contains__('18+'):  #Adult Pricing
        #         if reg.prereg_status == 'SUCCEEDED':   #Pre-reg Pricing
        #             # Calculate daily pricing for both Members and Non-Members
        #             if today <= opening_day: # Saturday or Earlier
        #                 price_calc = prereg_sat_price
        #             elif  today == opening_day + 1: # Sunday
        #                 price_calc = prereg_sun_price 
        #             elif  today == opening_day + 2: # Monday 
        #                 price_calc = prereg_mon_price
        #             elif  today == opening_day + 3: # Tuesday
        #                 price_calc = prereg_tue_price
        #             elif  today == opening_day + 4: # Wednesday
        #                 price_calc = prereg_wed_price 
        #             elif  today == opening_day + 5: # Thursday
        #                 price_calc = prereg_thur_price
        #             elif  today == opening_day + 6: # Friday
        #                 price_calc = prereg_fri_price
        #             elif  today == opening_day + 7: # Saturday2
        #                 price_calc = prereg_sat2_price
        #             else:
        #                 print('Error, arival date out of range')
        #         else:  # At the Door pricing
        #             # Calculate daily pricing for both Members and Non-Members
        #             if today <= opening_day: # Saturday or Earlier
        #                 price_calc = door_sat_price 
        #             elif  today == opening_day + 1: # Sunday
        #                 price_calc = door_sun_price 
        #             elif  today == opening_day + 2: # Monday 
        #                 price_calc = door_mon_price
        #             elif  today == opening_day + 3: # Tuesday
        #                 price_calc = door_tue_price
        #             elif  today == opening_day + 4: # Wednesday
        #                 price_calc = door_wed_price 
        #             elif  today == opening_day + 5: # Thursday
        #                 price_calc = door_thur_price
        #             elif  today == opening_day + 6: # Friday
        #                 price_calc = door_fri_price
        #             elif  today == opening_day + 7: # Saturday2
        #                 price_calc = door_sat2_price
        #             else:
        #                 print('Error, arival date out of range')    
        #         if rate_mbr == 'Non-Member':   # Add NMR to non members
        #             price_calc = price_calc + nmr
        #     elif rate_age == 'tour_adult':
        #         price_calc = 20
        #     elif rate_age == 'tour_teen':
        #         price_calc = 10
        #     else:  # Youth and Royal Pricing
        #         price_calc = 0

        medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()

        if medallion_check is not None and int(regid) != int(medallion_check.regid):
            flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.regid) )
            dup_url = '<a href=' + url_for('reg', regid=str(medallion_check.regid)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
            flash(Markup(dup_url))
        else:
            reg.medallion = medallion
            reg.rate_mbr = rate_mbr
            reg.rate_age = rate_age
            reg.kingdom = kingdom
            reg.checkin = datetime.today()
            reg.price_calc = calculate_price_calc(reg)
            #Calculate Price Due
            if price_paid > price_calc + reg.paypal_donation_amount:  #Account for people who showed up late.  No refund.
                reg.price_due = 0
            else:
                reg.price_due = (reg.price_calc + reg.paypal_donation_amount) - (reg.price_paid + reg.atd_paid)
                print("Calculating price:", reg.price_calc) 

            db.session.commit()

            print(reg)
            log_reg_action(reg, 'CHECKIN')

            return redirect(url_for('reg', regid=regid))

    return render_template('checkin.html', reg=reg, form=form)

@app.route('/full_signature_export', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def full_export():
    regs = query_db("SELECT * FROM registrations WHERE signature IS NOT NULL")
    return render_template('full_export_images.html', regs=regs)

@app.route('/reports', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin')
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

            file = 'full_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

            rptquery = "SELECT * FROM registrations"
            df = pd.read_sql_query(rptquery, engine)
            path1 = './reports/' + file
            path2 = '../reports/' + file
            
            df.to_csv(path1)
            
        if report_type == 'full_checkin_report':

            file = 'full_checkin_report_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

            rptquery = "SELECT * FROM registrations WHERE checkin::date BETWEEN {} and {}"
            rptquery = rptquery.format('%(start_date)s', '%(end_date)s')
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

            df = pd.read_sql("SELECT kingdom, checkin::date, COUNT(regid) FROM registrations WHERE checkin IS NOT NULL GROUP BY kingdom, checkin", engine)
            df_pivot = df.pivot_table(index='kingdom', columns='checkin', values='count', dropna=False)

            path1 = './reports/' + file
            path2 = '../reports/' + file

            writer = pd.ExcelWriter(path1, engine='xlsxwriter')

            # df_pivot.to_excel(writer, sheet_name='Report' ,index = True)

            out = df_pivot.assign(Total=df_pivot.sum(axis=1))
            out = pd.concat([out, out.sum().to_frame('Total').T])
            out.to_excel(writer, sheet_name='Report', index = True)
            workbook = writer.book
            worksheet = writer.sheets["Report"]

            writer.close()

        if report_type == 'earlyon':

            file = 'earlyon_list_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

            df = pd.read_sql("SELECT regid, invoice_paid, fname, lname, scaname, email, kingdom, lodging FROM registrations WHERE early_on = true", engine)

            path1 = './reports/' + file
            path2 = '../reports/' + file

            writer = pd.ExcelWriter(path1, engine='xlsxwriter')

            df.to_excel(writer, sheet_name='Report' ,index = False)

            writer.close()

        if report_type == 'ghost_report':

            file = 'ghost_report_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

            rptquery = "SELECT order_id, regid, fname, lname, scaname, rate_age, lodging, prereg_status, checkin FROM registrations WHERE prereg_status = {} AND checkin IS NULL ORDER BY lodging"
            rptquery = rptquery.format('%(prereg_status)s')
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
@login_required
@roles_accepted('Admin', "Troll Shift Lead", "Troll User")
def waiver():
    form = WaiverForm()
    regid = request.args['regid']
    reg = get_reg(regid)
    form.paypal_donation.data = reg.paypal_donation
    if request.method == 'POST':

        if reg.paypal_donation == False and bool(request.form.get('paypal_donation')) == True:
            reg.paypal_donation_amount = 3
        elif reg.paypal_donation == True and bool(request.form.get('paypal_donation')) == False:            
            reg.paypal_donation_amount = 0
        reg.paypal_donation = bool(request.form.get('paypal_donation'))
        reg.price_due = (reg.price_calc + reg.paypal_donation_amount) - reg.price_paid
        reg.signature = form.signature.data
        
        db.session.commit()

        log_reg_action(reg, 'WAIVER')

        return redirect(url_for('reg', regid=regid))

    return render_template('waiver.html', form=form, reg=reg)

@app.route('/payment', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "Troll User", "Troll Shift Lead")
def payment():
    form = EditForm()
    regid = request.args['regid']
    reg = get_reg(regid)
    form.fname.data = reg.fname
    form.lname.data = reg.lname
    form.scaname.data = reg.scaname
    form.invoice_email.data = reg.invoice_email
    form.price_calc.data = reg.price_calc
    form.price_due.data = reg.price_due
    form.pay_type.data = reg.atd_pay_type
    if request.method == 'POST':

        if request.form.get('pay_type') == '':
            flash('Must select a Payment Type')
            return redirect(url_for('payment', regid=regid, form=form))

        # reg.atd_paid = form.atd_paid.data
        # if reg.price_paid + reg.atd_paid > reg.price_calc:  #Account for people who showed up late.  No refund.
        #     reg.price_due = 0
        # else:
        #     reg.price_due = reg.price_calc - (reg.price_paid + reg.atd_paid)

        reg.atd_pay_type = request.form.get('pay_type')
        reg.atd_paid += reg.price_due
        reg.price_due = 0
        db.session.commit()

        log_reg_action(reg, 'PAYMENT')

        return redirect(url_for('reg', regid=regid))

    return render_template('payment.html', form=form)