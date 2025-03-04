from app import app, db, login
from app.forms import *
from app.models import *
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
import csv
import codecs
import requests

@login.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)
from collections import namedtuple
from sqlalchemy import or_, and_

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
    
def get_role_choices():
    roles = get_roles()
    role_choices = []
    role_dict = {}
    for r in roles:
        role_dict[r.name] = r

    if current_user.has_role('Admin'):
        for r in roles:
            role_choices.append([r.id, r.name])
        return role_choices
    
    if current_user.has_role('Marshal Admin'):
        role_choices.append([role_dict['Marshal User'].id,'Marshal User'])

    if current_user.has_role('Troll Shift Lead') or current_user.has_role('Department Head'):
        role_choices.append([role_dict['Troll User'].id,'Troll User'])
    
    if current_user.has_role('Department Head'):
        role_choices.append([role_dict['Troll Shift Lead'].id,'Troll Shift Lead'])

    return role_choices

def currentuser_has_permission_on_user(cuser, user):
    if cuser.has_role('Admin'):
        return True
    elif cuser.has_role('Marshal Admin') and user.has_role('Marshal User'):
        return True
    elif (cuser.has_role('Troll Shift Lead') or current_user.has_role('Department Head')) and user.has_role('Troll User'):
        return True
    elif current_user.has_role('Department Head') and user.has_role('Troll Shift Lead'):
        return True
    else:
        return False

def get_roles():
    roles = Role.query.all()
    if roles is None:
        abort(404)
    return roles

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

def currentuser_has_permission_on_user(cuser, user):
    if cuser.has_role('Admin'):
        return True
    elif cuser.has_role('Marshal Admin') and user.has_role('Marshal User'):
        return True
    elif cuser.has_role('Troll Shift Lead') and user.has_role('Troll User'):
        return True
    else:
        return False

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

def get_inspection_stats():
    inspection_stats = {}
    inspections = MartialInspection.query.all()
    ranged_inspections = Registrations.query.filter(or_(Registrations.crossbows != None, Registrations.bows != None)).all()

    chivalric_inspections = 0
    rapier_inspections = 0
    combat_archery = 0
    bow_inspections = 0
    crossbow_inspections = 0
    for i in inspections:

        match i.inspection_type:
            case 'Heavy':
                chivalric_inspections += 1
            case 'Heavy Spear':
                chivalric_inspections += 1
            case 'Rapier':
                rapier_inspections += 1
            case 'Rapier Spear':
                rapier_inspections += 1
            case 'Combat Archery':
                combat_archery += 1

    for i in ranged_inspections:
        if i.bows:
            bow_inspections += len(i.bows)
        if i.crossbows:
            crossbow_inspections += len(i.crossbows)

    inspection_stats = {
    'chivalric_inspections':chivalric_inspections, 
    'rapier_inspections':rapier_inspections, 
    'combat_archery_inspections':combat_archery,
    'bow_inspections':bow_inspections, 
    'crossbow_inspections':crossbow_inspections}
    return inspection_stats


def prereg_total():
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM registrations WHERE invoice_status IS NOT NULL AND invoice_status != 'DUPLICATE' AND invoice_status != 'CANCELED';", [])
    results = cur.fetchone()
    for preregcount in results:
        print(preregcount)
    conn.close()
    if preregcount is None:
        abort(404)
    return preregcount

def unsent_count():
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(DISTINCT invoice_email) FROM registrations WHERE invoice_status = 'UNSENT';", [])
    results = cur.fetchone()
    for unsentcount in results:
        print(unsentcount)
    conn.close()
    if unsentcount is None:
        abort(404)
    return unsentcount

def unsent_reg_count():
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM registrations WHERE invoice_status = 'UNSENT';", [])
    results = cur.fetchone()
    for unsentcount in results:
        print(unsentcount)
    conn.close()
    if unsentcount is None:
        abort(404)
    return unsentcount

def open_count():
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(DISTINCT invoice_number) FROM registrations WHERE invoice_status = 'SENT';", [])
    results = cur.fetchone()
    for opencount in results:
        print(opencount)
    conn.close()
    if opencount is None:
        abort(404)
    return opencount

def open_reg_count():
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM registrations WHERE invoice_status = 'SENT';", [])
    results = cur.fetchone()
    for opencount in results:
        print(opencount)
    conn.close()
    if opencount is None:
        abort(404)
    return opencount

def paid_count():
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(DISTINCT invoice_number) FROM registrations WHERE invoice_status = 'PAID';", [])
    results = cur.fetchone()
    for paidcount in results:
        print(paidcount)
    conn.close()
    if paidcount is None:
        abort(404)
    return paidcount

def paid_reg_count():
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM registrations WHERE invoice_status = 'PAID';", [])
    results = cur.fetchone()
    for paidcount in results:
        print(paidcount)
    conn.close()
    if paidcount is None:
        abort(404)
    return paidcount

def canceled_count():
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(DISTINCT invoice_number) FROM registrations WHERE invoice_status = 'CANCELED' OR invoice_status = 'DUPLICATE';", [])
    results = cur.fetchone()
    for canceledcount in results:
        print(canceledcount)
    conn.close()
    if canceledcount is None:
        abort(404)
    return canceledcount

def canceled_reg_count():
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM registrations WHERE invoice_status = 'CANCELED' OR invoice_status = 'DUPLICATE';", [])
    results = cur.fetchone()
    for canceledcount in results:
        print(canceledcount)
    conn.close()
    if canceledcount is None:
        abort(404)
    return canceledcount

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
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        if not user.active:
            flash('User is Inactive')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/martialhome', methods=['GET', 'POST'])
@roles_accepted('Admin','Marshal Admin','Marshal User')
def martialhome():
    # inspection_stats = get_inspection_stats()
    inspection_stats = None
    if request.method == "POST":
        print("SEARCHED")
        if request.form.get('search_name'):
            search_value = request.form.get('search_name')
            print(search_value)
            if search_value is not None and search_value != '':
                reg = query_db(
                    "SELECT * FROM registrations WHERE (fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s) AND checkin IS NOT NULL order by lname, fname",
                    #(search_value, search_value, search_value))
                    ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
            return render_template('martial_home.html', searchreg=reg, inspection_stats=inspection_stats)
        elif request.form.get('mbrnum_id'):
            search_value = request.form.get('mbrnum_id')
            reg = query_db(
                "SELECT * FROM registrations WHERE mbr_num = %s AND checkin IS NOT NULL order by lname, fname",
                (int(search_value),))
            return render_template('martial_home.html', searchreg=reg, inspection_stats=inspection_stats)
        elif request.form.get('medallion'):
            search_value = request.form.get('medallion')
            reg = query_db(
                "SELECT * FROM registrations WHERE medallion = %s order by lname, fname",
                (search_value,))
            return render_template('martial_home.html', searchreg=reg, inspection_stats=inspection_stats)
        else:
            return render_template('martial_home.html', inspection_stats=inspection_stats)
    else:
        return render_template('martial_home.html', inspection_stats=inspection_stats)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/myaccount', methods=['GET', 'POST'])
@login_required
def myaccount():
    checkedincount = len(RegLogs.query.filter(RegLogs.userid == current_user.id, RegLogs.action == 'CHECKIN').all())
    return render_template('myaccount.html', acc=current_user, checkedincount=checkedincount)

@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = UpdatePasswordForm()
    form.id.data = current_user.id
    form.username.data = current_user.username
    if request.method == 'POST' and form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash("Password Successfully Changed!")
        return redirect(url_for('myaccount'))
    elif request.method == 'POST' and not form.validate_on_submit():
        for field in form.errors:
            flash(form.errors[field])
        return render_template('changepassword.html', form=form, user=current_user)
    else:
        return render_template('changepassword.html', form=form, user=current_user)

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    regcount = reg_count()
    print(request.method)
    if request.method == "POST":
        print("SEARCHED")
        print(request.form.get('search_canceled'))
        if request.form.get('search_name'):
            search_value = request.form.get('search_name')
            print(search_value)
            if search_value is not None and search_value != '':
                if request.form.get('search_canceled'):
                    reg = query_db(
                        "SELECT * FROM registrations WHERE (fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s) AND (invoice_status NOT IN ('DUPLICATE','SENT','UNSENT') OR invoice_status IS NULL) order by checkin DESC, lname, fname",
                        #(search_value, search_value, search_value))
                        ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
                else:
                    reg = query_db(
                        "SELECT * FROM registrations WHERE (fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s) AND (invoice_status NOT IN ('DUPLICATE','CANCELED','SENT','UNSENT') OR invoice_status IS NULL) order by checkin DESC, lname, fname",
                        #(search_value, search_value, search_value))
                        ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
            return render_template('index.html', searchreg=reg, regcount=regcount)
        elif request.form.get('invoice_number'):
            search_value = request.form.get('invoice_number')
            if request.form.get('search_canceled'):
                reg = query_db(
                    "SELECT * FROM registrations WHERE invoice_number LIKE %s AND (invoice_status NOT IN ('DUPLICATE','SENT','UNSENT') OR invoice_status IS NULL) order by checkin DESC, lname, fname",
                    ('%' + search_value + '%',))
            else:
                reg = query_db(
                    "SELECT * FROM registrations WHERE invoice_number LIKE %s AND (invoice_status NOT IN ('DUPLICATE','CANCELED','SENT','UNSENT') OR invoice_status IS NULL) order by checkin DESC, lname, fname",
                    ('%' + search_value + '%',))
            return render_template('index.html', searchreg=reg, regcount=regcount)
        elif request.form.get('medallion'):
            search_value = request.form.get('medallion')
            reg = query_db(
                "SELECT * FROM registrations WHERE medallion = %s order by checkin DESC, lname, fname",
                (search_value,))
            return render_template('index.html', searchreg=reg, regcount=regcount)
    else:
        return render_template('index.html', regcount=regcount)

@app.route('/<int:regid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Troll Shift Lead','Troll User','Cashier','Department Head')
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
@roles_accepted('Admin','Invoices','Department Head')
def unsentinvoices():
    regs = Registrations.query.filter(and_(Registrations.invoice_number == None, Registrations.invoice_status != 'CANCELED', Registrations.invoice_status != 'DUPLICATE', Registrations.invoice_status != 'SENT', Registrations.invoice_status != 'PAID', Registrations.prereg_status == "SUCCEEDED")).order_by(Registrations.invoice_email).all()
    preregtotal = prereg_total()
    invoicecount = unsent_count()
    regcount = unsent_reg_count()
    return render_template('invoice_list.html', regs=regs, preregtotal=preregtotal, invoicecount=invoicecount, regcount=regcount, back='unsent')

@app.route('/invoice/open', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def openinvoices():
    regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.prereg_status == "SUCCEEDED", Registrations.invoice_status == 'SENT')).order_by(Registrations.invoice_email).all()
    preregtotal = prereg_total()
    invoicecount = open_count()
    regcount = open_reg_count()
    return render_template('invoice_list.html', regs=regs, preregtotal=preregtotal, invoicecount=invoicecount, regcount=regcount, back='open')

@app.route('/invoice/paid', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def paidinvoices():
    regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.prereg_status == "SUCCEEDED", Registrations.invoice_status == 'PAID')).order_by(Registrations.invoice_email).all()
    preregtotal = prereg_total()
    invoicecount = paid_count()
    regcount = paid_reg_count()
    return render_template('invoice_list.html', regs=regs, preregtotal=preregtotal, invoicecount=invoicecount, regcount=regcount, back='paid')

@app.route('/invoice/canceled', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def canceledinvoices():
    regs = Registrations.query.filter(and_(Registrations.prereg_status == "SUCCEEDED", or_(Registrations.invoice_status == 'CANCELED', Registrations.invoice_status == 'DUPLICATE'))).order_by(Registrations.invoice_email).all()
    preregtotal = prereg_total()
    invoicecount = canceled_count()
    regcount = canceled_reg_count()
    return render_template('invoice_list.html', regs=regs, preregtotal=preregtotal, invoicecount=invoicecount, regcount=regcount, back='canceled')

@app.route('/invoice/all', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def allinvoices():
    regs = Registrations.query.filter(Registrations.prereg_status == "SUCCEEDED").order_by(Registrations.invoice_email).all()
    now = datetime.now()
    return render_template('invoice_list.html', regs=regs, back='all', now=now)

@app.route('/invoice/<int:regid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
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
    form.duplicate_invoice.data = True if reg.invoice_status == 'DUPLICATE' else False
    form.is_check.data = True if reg.pay_type == 'check' else False
    form.notes.data = reg.notes
    
    if request.method == 'POST':
        invoice_number = request.form.get('invoice_number')
        price_paid = int(request.form.get('price_paid'))
        price_calc = int(request.form.get('price_calc'))
        invoice_date = request.form.get('invoice_date')
        invoice_payment_date = request.form.get('invoice_payment_date')
        invoice_canceled = bool(request.form.get('invoice_canceled'))

        #if is_duplicate_invoice_number(invoice_number, reg):
        #    flash('Duplicate Invoice Number {}'.format(
        #    invoice_number))
        #    return render_template('update_invoice.html', reg=reg, form=form)
        
        if invoice_number is not None and invoice_number != '':
            reg.invoice_status = 'SENT'
        if int(price_paid) >= int(price_calc) + int(reg.paypal_donation_amount):
            reg.invoice_status = 'PAID'
        if bool(request.form.get('invoice_canceled')) == True:
            reg.invoice_status = 'CANCELED'
        if bool(request.form.get('duplicate_invoice')) == True:
            reg.invoice_status = 'DUPLICATE'

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

        if bool(request.form.get('is_check')) == True:
            reg.pay_type = 'check'
        else:
            reg.pay_type = 'paypal'
        
        reg.notes = request.form.get('notes')

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
            case 'all': 
                return redirect('/invoice/all')
            case _:
                return redirect('/')


    return render_template('update_invoice.html', reg=reg, form=form)


@app.route('/role/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def createrole():
    form = CreateRoleForm()
    all_roles = Role.query.filter(Role.id is not None).all()
    if request.method == 'POST':
        role = Role(id = request.form.get('id') ,name=request.form.get('role_name'))
        db.session.add(role)
        db.session.commit()
        return redirect('/')
    return render_template('createrole.html', form=form, roles=all_roles)
    
@app.route('/martial/<int:regid>/addbow', methods=('GET', 'POST'))
@roles_accepted('Admin','Marshal Admin','Marshal User')
def add_bow(regid):
    reg = get_reg(regid)
    form = BowForm()
    if request.method == 'POST':
        if request.form.get("poundage"):
            update_reg = Registrations.query.filter_by(regid=reg.regid).first()
            bow = Bows()
            bow.poundage = request.form.get("poundage")
            bow.bow_inspection_martial_id = current_user.id
            bow.bow_inspection_date = datetime.now()
            if update_reg.bows:
                update_reg.bows.append(bow)
            else:
                bows = []
                bows.append(bow)
                update_reg.bows = bows
            db.session.commit()
        return redirect(url_for('martial_reg', regid=regid))
    return render_template('add_bow.html', reg=reg, form=form)

@app.route('/martial/<int:regid>/addcrossbow', methods=('GET', 'POST'))
@roles_accepted('Admin','Marshal Admin','Marshal User')
def add_crossbow(regid):
    reg = get_reg(regid)
    form = BowForm()
    if request.method == 'POST':
        print('POSTED')
        if request.form.get("poundage"):
            print('Poundage')
            print(request.form.get("poundage"))
            update_reg = Registrations.query.filter_by(regid=reg.regid).first()
            print(request.form.get("poundage"))
            crossbow = Crossbows()
            crossbow.inchpounds = request.form.get("poundage")
            crossbow.crossbow_inspection_martial_id = current_user.id
            crossbow.crossbow_inspection_date = datetime.now()
            if update_reg.crossbows:
                update_reg.crossbows.append(crossbow)
            else:
                crossbows = []
                crossbows.append(crossbow)
                update_reg.crossbows = crossbows
            print('YEP')
            db.session.commit()
        return redirect(url_for('martial_reg', regid=regid))
    return render_template('add_crossbow.html', reg=reg, form=form)

@app.route('/martial/<int:regid>/addincident', methods=('GET', 'POST'))
@roles_accepted('Admin','Marshal Admin','Marshal User')
def add_incident(regid):
    reg = get_reg(regid)
    form = IncidentForm()
    if request.method == 'POST':
        incident_date = request.form.get("incident_date")
        notes = request.form.get("notes")

        new_incident = IncidentReport(
            regid = regid,
            report_date = datetime.now(),
            incident_date = incident_date,
            reporting_user_id = current_user.id,
            notes = notes
        )

        db.session.add(new_incident)
        db.session.commit()

        return redirect(url_for('martial_reg', regid=regid))
    return render_template('add_crossbow.html', reg=reg, form=form)

@app.route('/martial/<int:regid>', methods=('GET', 'POST'))
@roles_accepted('Admin','Marshal Admin','Marshal User')
def martial_reg(regid):
    reg = get_reg(regid)
    print(reg.incident_report)
    form = MartialForm()
    bow_form = BowForm()
    incident_form = IncidentForm()
    url = f"https://amp.ansteorra.org/activities/authorizations/getMemberAuthorizations/{reg.email}"
    headers = {
                'Authorization': 'gw_gate|VN7xw8nutVx232KFKESjnKs46Kgrr4XaHqcnkjh773pEB5Sszw'
                }
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        fighter_auth = response.json()
    else:
        fighter_auth = None
    print(response.status_code)
    inspections = MartialInspection.query.filter(MartialInspection.regid == regid).all()
    inspection_dict = {}
    for inspection in inspections:
        inspection_dict[inspection.inspection_type] = inspection
        match inspection.inspection_type:
            case 'Heavy':
                form.chivalric_inspection.data = inspection.inspected
            case 'Heavy Spear':
                form.chivalric_spear_inspection.data = inspection.inspected
            case 'Rapier':
                form.rapier_inspection.data = inspection.inspected
            case 'Rapier Spear':
                form.rapier_spear_inspection.data = inspection.inspected
            case 'Combat Archery':
                form.combat_archery_inspection.data = inspection.inspected

    if reg.bows:
        for bow in reg.bows:
            form.bows.append_entry(bow)
    if reg.crossbows:
        for crossbow in reg.crossbows:
            form.crossbows.append_entry(crossbow)

    if request.method == 'POST':
        chivalric_inspection = request.form.get('chivalric_inspection')
        chivalric_spear_inspection = request.form.get('chivalric_spear_inspection')
        rapier_inspection = request.form.get('rapier_inspection')
        rapier_spear_inspection = request.form.get('rapier_spear_inspection')
        combat_archery_inspection = request.form.get('combat_archery_inspection')

        if 'Heavy' not in inspection_dict and chivalric_inspection:
            new_inspection = MartialInspection(
                regid = regid,
                inspection_type = 'Heavy',
                inspection_date = datetime.now(),
                inspecting_martial_id = current_user.id,
                inspected = True
            )
            db.session.add(new_inspection)
        if 'Heavy Spear' not in inspection_dict and chivalric_spear_inspection:
            new_inspection = MartialInspection(
                regid = regid,
                inspection_type = 'Heavy Spear',
                inspection_date = datetime.now(),
                inspecting_martial_id = current_user.id,
                inspected = True
            )
            db.session.add(new_inspection)
        if 'Rapier' not in inspection_dict and rapier_inspection:
            new_inspection = MartialInspection(
                regid = regid,
                inspection_type = 'Rapier',
                inspection_date = datetime.now(),
                inspecting_martial_id = current_user.id,
                inspected = True
            )
            db.session.add(new_inspection)
        if 'Rapier Spear' not in inspection_dict and rapier_spear_inspection:
            new_inspection = MartialInspection(
                regid = regid,
                inspection_type = 'Rapier Spear',
                inspection_date = datetime.now(),
                inspecting_martial_id = current_user.id,
                inspected = True
            )
            db.session.add(new_inspection)
        if 'Combat Archery' not in inspection_dict and combat_archery_inspection:
            new_inspection = MartialInspection(
                regid = regid,
                inspection_type = 'Combat Archery',
                inspection_date = datetime.now(),
                inspecting_martial_id = current_user.id,
                inspected = True
            )
            db.session.add(new_inspection)

        db.session.commit()
        return redirect(url_for('martial_reg',regid=regid))
    return render_template('martial_reg.html', reg=reg, form=form, bow_form=bow_form, inspection_dict=inspection_dict, incident_form=incident_form, fighter_auth=fighter_auth)

@app.route('/martial/reports', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Marshal Admin')
def martialreports():
    form = ReportForm()
    form.report_type.choices = [('full_inspection_report','full_inspection_report'),('full_incident_report','full_incident_report')]
    s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
    conndict = dict(item.split("=") for item in s.split(" "))
    connstring = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
    engine=db.create_engine(connstring)
    
    file = 'test_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_")) + '.xlsx'
   
    report_type = form.report_type.data

    if report_type == 'full_inspection_report':

        file = 'full_inspection_report_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        rptquery = "SELECT regid, (SELECT fname FROM registrations WHERE registrations.regid = martial_inspection.regid) AS \"Reg_FName\", (SELECT lname FROM registrations WHERE registrations.regid = martial_inspection.regid) AS \"Reg_LName\", inspection_type, inspection_date, (SELECT fname FROM users WHERE users.id = martial_inspection.inspecting_martial_id) AS \"Marshal_FName\", (SELECT lname FROM users WHERE users.id = martial_inspection.inspecting_martial_id) AS \"Marshal_LName\", (SELECT medallion FROM users WHERE users.id = martial_inspection.inspecting_martial_id) AS \"Marshal_Medallion\" FROM martial_inspection"
        df = pd.read_sql_query(rptquery, engine)
        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        writer = pd.ExcelWriter(path1, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Report' ,index = False)
        worksheet = writer.sheets['Report']
        writer.close()
        return send_file(path2)
    
    if report_type == 'full_incident_report':

        file = 'full_incident_report_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        rptquery = "SELECT regid, (SELECT fname FROM registrations WHERE registrations.regid = incidentreport.regid) AS \"Reg_FName\", (SELECT lname FROM registrations WHERE registrations.regid = incidentreport.regid) AS \"Reg_LName\", report_date, incident_date, (SELECT fname FROM users WHERE users.id = incidentreport.reporting_user_id) AS \"Marshal_FName\", (SELECT lname FROM users WHERE users.id = incidentreport.reporting_user_id) AS \"Marshal_LName\", notes FROM incidentreport"
        df = pd.read_sql_query(rptquery, engine)
        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        writer = pd.ExcelWriter(path1, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Report' ,index = False)
        worksheet = writer.sheets['Report']
        writer.close()
        return send_file(path2)
    return render_template('reports.html', form=form)


@app.route('/users', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Marshal Admin','Troll Shift Lead','Department Head')
def users():
    return_users = []
    users = User.query.all()
    if current_user.has_role('Admin'):
        return render_template('users.html', users=users)
    
    for user in users:
        if current_user.has_role('Marshal Admin') and user.has_role('Marshal User'):
            return_users.append(user)

        if (current_user.has_role('Troll Shift Lead') or current_user.has_role('Department Head')) and user.has_role('Troll User'):
            return_users.append(user)
        
        if current_user.has_role('Department Head') and user.has_role('Troll Shift Lead'):
            return_users.append(user)

    return render_template('users.html', users=return_users)


@app.route('/user/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Marshal Admin','Troll Shift Lead','Department Head')
def createuser():

    form = CreateUserForm()
    form.role.choices = get_role_choices()
    
    if request.method == 'POST':
        dup_user_check = User.query.filter(User.username == form.username.data).first()
        if dup_user_check:
            flash("Username Already Taken - Please Try Again")
            return render_template('createuser.html', form=form)
        user = User()
        user.username = form.username.data
        for roleid in form.role.data:
            user.roles.append(get_role(roleid))
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.medallion = form.medallion.data
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
@roles_accepted('Admin','Marshal Admin','Troll Shift Lead','Department Head')
def edituser():
    user = get_user(request.args.get("userid"))
    if not currentuser_has_permission_on_user(current_user,user):
        return redirect('/users')
    if not currentuser_has_permission_on_user(current_user,user):
        return redirect('/users')
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
            medallion = user.medallion,
            active = user.active
        )
        form.role.choices = get_role_choices()
        
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
        user.medallion = form.medallion.data
        user.medallion = form.medallion.data
        user.active = bool(request.form.get('active'))

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
    # Close Pre-Reg at Midnight 02/22/2025
    if datetime.now().date() >= datetime.strptime('02/22/2025','%m/%d/%Y').date():
        return render_template("prereg_closed.html")

    form = CreatePreRegForm()

    loading_df = pd.read_csv('gwlodging.csv')
    lodgingdata = loading_df.to_dict(orient='list')
    form.lodging.choices = lodgingdata

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
            royal_departure_date = form.royal_departure_date.data,
            royal_title = form.royal_title.data if form.royal_title.data != '' else None
        )

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
@roles_accepted('Admin','Troll Shift Lead','Troll User','Department Head')
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
        mbr_num = form.mbr_num.data,
        mbr_num_exp = form.mbr_num_exp.data,
        city = form.city.data,
        state_province = form.state_province.data,
        zip = form.zip.data,
        country = form.country.data,
        phone = form.phone.data,
        email = form.email.data,
        invoice_email = form.invoice_email.data,
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
        reg.rate_date = datetime.now().date()
        reg.price_calc = calculate_price_calc(reg)
        if reg.price_paid + reg.atd_paid > reg.price_calc:  #Account for people who showed up late.  No refund.
            reg.price_due = 0
        else:
            reg.price_due = reg.price_calc - (reg.price_paid + reg.atd_paid)

        if form.rate_mbr.data == 'Member':
            if datetime.strptime(request.form.get('mbr_num_exp'),'%Y-%m-%d').date() < datetime.now().date():
                flash('Membership Expiration Date {} is not current.'.format(form.mbr_num_exp.data))
                return render_template('create.html', title = 'New Registration', form=form)

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
@roles_accepted('Admin', 'Troll Shift Lead','Department Head')
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
        mbr_num_exp = datetime.strptime(reg.mbr_num_exp, '%Y-%m-%d') if reg.mbr_num_exp is not None else None,
        onsite_contact_name = reg.onsite_contact_name,
        onsite_contact_sca_name = reg.onsite_contact_sca_name,
        onsite_contact_kingdom = reg.onsite_contact_kingdom,
        onsite_contact_group = reg.onsite_contact_group,
        offsite_contact_name = reg.offsite_contact_name,
        offsite_contact_phone = reg.offsite_contact_phone,
        notes = reg.notes
    )

    if reg.rate_date != None:
        try:
            form.rate_date.data = datetime.strptime(reg.rate_date, '%Y-%m-%d %H:%M:%S')
        except:
            form.rate_date.data = datetime.strptime(reg.rate_date, '%Y-%m-%d')

    loading_df = pd.read_csv('gwlodging.csv')
    lodgingdata = loading_df.to_dict(orient='list')
    form.lodging.choices = lodgingdata

    if request.method == 'POST':

        if current_user.has_role('Troll Shift Lead'):
            reg.notes = request.form.get('notes')
            if request.form.get('medallion') != '' and request.form.get('medallion') != None:
                medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()
            else:
                medallion_check = None

            if medallion_check is not None and int(regid) != int(medallion_check.regid):
                flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.regid) )
                dup_url = '<a href=' + url_for('reg', regid=str(medallion_check.regid)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
                flash(Markup(dup_url))
            else:
                if request.form.get('medallion'):
                    reg.medallion = int(request.form.get('medallion'))
                else: reg.medallion = None

                reg.rate_mbr = request.form.get('rate_mbr')
                if request.form.get('mbr_num'):
                    reg.mbr_num = int(request.form.get('mbr_num'))
                else: reg.mbr_num = None

                if request.form.get('mbr_num_exp'):
                    reg.mbr_num_exp = request.form.get('mbr_num_exp')

                db.session.commit()

                log_reg_action(reg, 'EDIT')

                return redirect(url_for('reg',regid=regid))
            
        else:

            reg.notes = request.form.get('notes')

            if request.form.get('medallion') != '' and request.form.get('medallion') != None:
                medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()
            else:
                medallion_check = None

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
                reg.rate_date = datetime.strptime(request.form.get('rate_date'), '%Y-%m-%d') if (request.form.get('rate_date') != '' and request.form.get('rate_date')) else None
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
                if request.form.get('mbr_num_exp'):
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
@roles_accepted('Admin','Troll Shift Lead','Troll User','Department Head')
def checkin():
    regid = request.args['regid']
    reg = get_reg(regid)

    form = CheckinForm(kingdom = reg.kingdom, rate_mbr = reg.rate_mbr, medallion = reg.medallion, rate_age = reg.rate_age, lodging = reg.lodging, notes=reg.notes, mbr_num=reg.mbr_num)
    if reg.mbr_num_exp is not None:
        form.mbr_num_exp.data = datetime.strptime(reg.mbr_num_exp, '%Y-%m-%d')
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
        if form.rate_mbr.data == 'Member':
            if request.form.get('mbr_num_exp') is None:
                flash('Membership Number is Required if Member.'.format(request.form.get('mbr_num_exp')))
                return render_template('checkin.html', reg=reg, form=form) 
            if request.form.get('mbr_num_exp') is None:
                flash('Membership Expiration Date is Required if Member.'.format(request.form.get('mbr_num_exp')))
                return render_template('checkin.html', reg=reg, form=form)
            if request.form.get('mbr_num_exp') is None or datetime.strptime(request.form.get('mbr_num_exp'),'%Y-%m-%d').date() < datetime.now().date():
                flash('Membership Expiration Date {} is not current.'.format(request.form.get('mbr_num_exp')))
                return render_template('checkin.html', reg=reg, form=form)
        medallion = form.medallion.data
        kingdom = form.kingdom.data
        rate_mbr = form.rate_mbr.data
        lodging = form.lodging.data
        minor_waiver = form.minor_waiver.data
        
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

        # UNCOMMENT ONCE DB UPDATED - MINOR WAIVER STATUS
        if form.minor_waiver.data == '-':
            flash('You must select a Minor Waiver Validation')
            return render_template('checkin.html', reg=reg, form=form)

        if request.form.get('medallion') != '' and request.form.get('medallion') != None:
            medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()
        else:
            medallion_check = None

        if medallion_check is not None and int(regid) != int(medallion_check.regid):
            duplicate_name = medallion_check.fname + " " + medallion_check.lname
            dup_url = '<a href=' + url_for('reg', regid=str(medallion_check.regid)) + f' target="_blank" rel="noopener noreferrer">{duplicate_name}</a>'
            flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " +  Markup(dup_url))
        else:
            #Account for PreReg Non-Member and Checkin Member (No NMR Refund - View as Donation)
            if reg.rate_mbr != 'Member' and rate_mbr == 'Member' and reg.prereg_status == 'SUCCEEDED' and reg.rate_age.__contains__('18+'):
                nmr_donation = 10
            else:
                nmr_donation = 0
            reg.medallion = medallion
            reg.rate_mbr = rate_mbr
            reg.rate_age = rate_age
            reg.kingdom = kingdom
            # UNCOMMENT ONCE DB UPDATED - MINOR WAIVER STATUS
            reg.minor_waiver = minor_waiver
            reg.lodging = lodging
            reg.checkin = datetime.today()
            reg.price_calc = calculate_price_calc(reg)
            reg.nmr_donation = nmr_donation
            reg.notes = form.notes.data

            #Calculate Price Due
            if price_paid > price_calc + reg.paypal_donation_amount:  #Account for people who showed up late.  No refund.
                reg.price_due = 0
            else:
                reg.price_due = (reg.price_calc + reg.paypal_donation_amount) - (reg.price_paid + reg.atd_paid)
                print("Calculating price:", reg.price_calc) 

            db.session.commit()

            log_reg_action(reg, 'CHECKIN')

            return redirect(url_for('reg', regid=regid))

    return render_template('checkin.html', reg=reg, form=form)

@app.route('/full_signature_export', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Department Head','Invoices')
def full_export():
    regs = query_db("SELECT * FROM registrations WHERE signature IS NOT NULL")
    return render_template('full_export_images.html', regs=regs)

@app.route('/reports', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin','Department Head','Invoices')
def reports():
    form = ReportForm()
    s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
    conndict = dict(item.split("=") for item in s.split(" "))
    connstring = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
    engine=db.create_engine(connstring)
    
    file = 'test_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_")) + '.xlsx'
    #if form.dt_start.data is not None:
    start_date = form.dt_start.data
    #if form.dt_end.data is not None:
    end_date = form.dt_end.data
   
    report_type = form.report_type.data

    if report_type == 'full_signatue_export':
        regs = query_db("SELECT * FROM registrations WHERE signature IS NOT NULL")
        return render_template('full_export_images.html', regs=regs)
    
    if report_type == 'full_export':

        file = 'full_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT * FROM registrations"
        df = pd.read_sql_query(rptquery, engine)
        base_price_list = []
        nmr_list = []
        for index, row in df.iterrows():
            if row['rate_mbr'] == 'Non-Member' and row['price_calc'] != 0 and row['rate_age'].__contains__('18+'):
                base_price_list.append(row['price_calc'] - 10)
                nmr_list.append(10)
            else:
                base_price_list.append(row['price_calc'])
                nmr_list.append(0)
        df['nmr'] = nmr_list
        df['base_price'] = base_price_list
        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)
        
    if report_type == 'full_checkin_report':
        if form.validate_on_submit():

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
            return send_file(path2)
    
    if report_type == 'at_door_count':
        if form.validate_on_submit():
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
            return send_file(path2)
    
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
        return send_file(path2)

    if report_type == 'earlyon':

        file = 'earlyon_list_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        df = pd.read_sql("SELECT regid, invoice_status, fname, lname, scaname, email, kingdom, lodging FROM registrations WHERE early_on = true and invoice_status = 'PAID'", engine)

        for index, row in df.iterrows():
            row['fname'] = row['fname'].strip()
            row['lname'] = row['lname'].strip()
            row['scaname'] = row['scaname'].strip() if row['scaname'] is not None else row['scaname']

                

        path1 = './reports/' + file
        path2 = '../reports/' + file

        writer = pd.ExcelWriter(path1, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='Report' ,index = False)

        writer.close()
        return send_file(path2)

    if report_type == 'ghost_report':

        file = 'ghost_report_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        rptquery = "SELECT invoice_number, regid, fname, lname, scaname, rate_age, lodging, invoice_status, checkin FROM registrations WHERE prereg_status = {} AND checkin IS NULL ORDER BY lodging"
        rptquery = rptquery.format('%(prereg_status)s')
        params = {'prereg_status':"SUCCEEDED"}
        df = pd.read_sql_query(rptquery, engine, params=params)
        path1 = './reports/' + file
        path2 = '../reports/' + file

        writer = pd.ExcelWriter(path1, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='Report' ,index = False)
        writer.close()
        return send_file(path2)

    if report_type == 'royal_registrations':

        file = 'royal_registrations_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        df = pd.read_sql("SELECT * FROM registrations WHERE rate_age = 'Royals'", engine)

        path1 = './reports/' + file
        path2 = '../reports/' + file

        writer = pd.ExcelWriter(path1, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='Report' ,index = False)

        writer.close()
        return send_file(path2)

    if report_type == 'land_pre-reg':

        file = 'land_pre-reg_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        df = pd.read_sql("SELECT lodging, invoice_number, regid, fname, lname, scaname, rate_age, invoice_status FROM registrations WHERE invoice_status = 'PAID' ORDER BY lodging, invoice_number", engine)

        path1 = './reports/' + file
        path2 = '../reports/' + file

        writer = pd.ExcelWriter(path1, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='Report' ,index = False)

        writer.close()
        return send_file(path2)


    if report_type == 'paypal_paid_export':

        file = 'paypal_paid_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT invoice_number, invoice_email, invoice_status, invoice_payment_date, rate_mbr, rate_age, price_paid, paypal_donation_amount, notes FROM registrations WHERE invoice_status = 'PAID'"
        df = pd.read_sql_query(rptquery, engine)
        base_price_list = []
        nmr_list = []
        for index, row in df.iterrows():
            if row['rate_mbr'] == 'Non-Member' and row['price_paid'] != 0 and row['rate_age'].__contains__('18+'):
                base_price_list.append(row['price_paid'] - 10 - row['paypal_donation_amount'])
                nmr_list.append(10)
            else:
                base_price_list.append(row['price_paid'] - row['paypal_donation_amount'])
                nmr_list.append(0)
        df['nmr'] = nmr_list
        df['base_price'] = base_price_list
        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)
    
    if report_type == 'paypal_canceled_export':

        file = 'paypal_cenceled_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT invoice_number, invoice_email, invoice_status, invoice_payment_date, rate_mbr, rate_age, price_paid, price_due, paypal_donation_amount, notes FROM registrations WHERE invoice_status = 'CANCELED'"
        df = pd.read_sql_query(rptquery, engine)
        base_price_list = []
        nmr_list = []
        for index, row in df.iterrows():

            if row['price_paid'] != 0:
                if row['rate_mbr'] == 'Non-Member' and row['price_paid'] != 0 and row['rate_age'].__contains__('18+'):
                    base_price_list.append(row['price_paid'] - 10 - row['paypal_donation_amount'])
                    nmr_list.append(10)
                else:
                    base_price_list.append(row['price_paid'] - row['paypal_donation_amount'])
                    nmr_list.append(0)
            else:
                if row['rate_mbr'] == 'Non-Member' and row['price_due'] != 0 and row['rate_age'].__contains__('18+'):
                    base_price_list.append(row['price_due'] - 10 - row['paypal_donation_amount'])
                    nmr_list.append(10)
                else:
                    base_price_list.append(row['price_due'] - row['paypal_donation_amount'])
                    nmr_list.append(0)
        df['nmr'] = nmr_list
        df['base_price'] = base_price_list
        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)
    
    if report_type == 'paypal_recon_export':


        invoice_nums = []
        paypal_invoice_nums = []
        counts = []
        counts_obj = {}
        dirty_obj = {}
        errors = []

        paypal_recon_file = request.files['paypal_file']

        merchant_df = pd.read_csv('merchant_fees.csv')
        merchant_dict = merchant_df.to_dict(orient='records')
        merchant_dict_exclude = {}

        for merchant in merchant_dict:
            for col in merchant:
                if not isinstance(merchant[col], int):
                     merchant[col] = float(merchant[col])
                merchant_dict_exclude[merchant['Invoice Number']] = merchant

        # csv_reader = csv.DictReader(paypal_recon_file)
        csv_reader = csv.DictReader(codecs.iterdecode(paypal_recon_file, 'utf-8'))

        for row in csv_reader:
            for col in row:
                if row[col].strip().startswith('$'):
                    row[col] = row[col].strip().replace("$","").replace("(","").replace(")","").replace(",","").replace("-","").replace("'",'').replace('"','')
                    if row[col].strip() != '':
                        row[col] = float(row[col].strip())
                    else: 
                        row[col] = 0
            dirty_obj[row['Invoice Number']] = row
            invoice_nums.append("'"+str(row['Invoice Number'])+"'")
            paypal_invoice_nums.append(str(row['Invoice Number']))

        for row in dirty_obj:
            counts_obj[row] = {
                'Date':None,
                'Time':None,
                'Name':'',
                'From Email Address':'',
                'Invoice Number':'',
                'Gross':0.00,
                'Fee':0.00,
                'Net':0.00,
                'Balance':0.00,
                'price_paid':0.00,
                'paypal_donation_amount':0.00,
                'nmr':0,
                'base_price':0.00,
                'expected_fee':0.00,
                'is_merchant':False,
                'To Email Address':'',
                'Transaction ID':'',
                'CounterParty Status':'',
                'Address Status':'',
                'Item Title':'',
                'Reference Txn ID':'',
                'Receipt ID':'',
                'Contact Phone Number':'',
                'Subject':'',
                'Payment Source':''
            }
            for col in dirty_obj[row].keys():
                if col == '\ufeff"Date"':
                    counts_obj[row]['Date'] = dirty_obj[row][col]
                if col not in ['TimeZone','Status','Currency','Note','Card Type','Type','Transaction Event Code','Balance Impact','\ufeff"Date"']:
                    if col in ['Gross','Fee','Net']:
                        dirty_obj[row][col] = dirty_obj[row][col].strip().replace("$","").replace("(","").replace(")","").replace(",","").replace("-","").replace("'",'')
                        counts_obj[row][col.strip()] = float(dirty_obj[row][col].strip())
                    else:
                        counts_obj[row][col.strip()] = dirty_obj[row][col]

        invoice_nums_str = ','.join(invoice_nums)

        file = 'paypal_recon_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        rptquery = f"SELECT invoice_number, invoice_email, invoice_status, invoice_payment_date, rate_mbr, rate_age, price_paid, paypal_donation_amount FROM registrations WHERE pay_type = 'paypal' AND (invoice_status = 'PAID' or invoice_status = 'CANCELED') AND invoice_number IN ({invoice_nums_str})"
        df = pd.read_sql_query(rptquery, engine)
        base_price_list = []
        nmr_list = [] 
        checks_list = []
        found_invoices = []

        for index, row in df.iterrows():
            found_invoices.append(row['invoice_number'])
            if row['rate_mbr'] == 'Non-Member' and row['price_paid'] != 0 and row['rate_age'].__contains__('18+'):
                base_price_list.append(row['price_paid'] - 10 - row['paypal_donation_amount'])
                nmr_list.append(10)
                row['base_price'] = row['price_paid'] - 10 - row['paypal_donation_amount']
                row['nmr'] = 10
            else:
                base_price_list.append(row['price_paid'] - row['paypal_donation_amount'])
                nmr_list.append(0)
                row['base_price'] = row['price_paid'] - row['paypal_donation_amount']
                row['nmr'] = 0

            if row['invoice_number'] not in counts_obj:
                obj = {'price_paid':float(row['price_paid']),'paypal_donation_amount':row['paypal_donation_amount'],'nmr':row['nmr'],'base_price':row['base_price']}
                counts_obj[row['invoice_number']] = obj
            else:
                counts_obj[row['invoice_number']]['price_paid'] += round(float(row['price_paid']),2)
                counts_obj[row['invoice_number']]['paypal_donation_amount'] += row['paypal_donation_amount']
                counts_obj[row['invoice_number']]['nmr'] += row['nmr']
                counts_obj[row['invoice_number']]['base_price'] += row['base_price']

        df['nmr'] = nmr_list
        df['base_price'] = base_price_list

        for obj in counts_obj:
            if obj != '' and obj is not None:
                if int(obj) in merchant_dict_exclude:
                    counts_obj[obj]['price_paid'] = merchant_dict_exclude[int(obj)]['Gross']
                    counts_obj[obj]['expected_fee'] = merchant_dict_exclude[int(obj)]['Fee']
                    counts_obj[obj]['is_merchant'] = True
                else:
                    if counts_obj[obj]['price_paid'] != 0:
                        expected_fee = round(counts_obj[obj]['price_paid'] * 0.0199 + 0.49,2)
                    else:
                        expected_fee = 0.00
                    counts_obj[obj]['expected_fee'] = expected_fee
                    if counts_obj[obj]['price_paid'] != counts_obj[obj]['Gross']:
                        errors.append({"Invoice Number":obj,'Error':"GROSS DOES NOT MATCH PRICE PAID",'PayPal': counts_obj[obj]['Gross'],'Export':counts_obj[obj]['price_paid'],'Email':counts_obj[obj]['From Email Address']})
                    if expected_fee != counts_obj[obj]['Fee']:
                        errors.append({"Invoice Number":obj,'Error':"EXPECTED FEE DOES NOT MATCH PAYPAL",'PayPal': counts_obj[obj]['Fee'],'Export':expected_fee,'Email':counts_obj[obj]['From Email Address']})
                counts.append(counts_obj[obj])
        
        rptquery = f"SELECT invoice_number, invoice_email, invoice_status, invoice_payment_date, rate_mbr, rate_age, price_paid, paypal_donation_amount FROM registrations WHERE pay_type = 'check' AND invoice_status = 'PAID'"
        df = pd.read_sql_query(rptquery, engine)

        for index, row in df.iterrows():
            if row['rate_mbr'] == 'Non-Member' and row['price_paid'] != 0 and row['rate_age'].__contains__('18+'):
                base_price_list.append(row['price_paid'] - 10 - row['paypal_donation_amount'])
                nmr_list.append(10)
                row['base_price'] = row['price_paid'] - 10 - row['paypal_donation_amount']
                row['nmr'] = 10
            else:
                base_price_list.append(row['price_paid'] - row['paypal_donation_amount'])
                nmr_list.append(0)
                row['base_price'] = row['price_paid'] - row['paypal_donation_amount']
                row['nmr'] = 0
            checks_list.append(row)
        
        unmatched_invoices = []
        for paypal_invoice_num in paypal_invoice_nums:
            if paypal_invoice_num not in found_invoices and paypal_invoice_num != '':
                rptquery = f"SELECT invoice_number, invoice_email, invoice_status, invoice_payment_date, rate_mbr, rate_age, price_paid, paypal_donation_amount FROM registrations WHERE pay_type = 'paypal' AND invoice_status = 'PAID' AND invoice_number LIKE '%%{paypal_invoice_num}%%'"
                df = pd.read_sql_query(rptquery, engine)
                for index, row in df.iterrows():
                    if row['rate_mbr'] == 'Non-Member' and row['price_paid'] != 0 and row['rate_age'].__contains__('18+'):
                        row['base_price'] = row['price_paid'] - 10 - row['paypal_donation_amount']
                        row['nmr'] = 10
                    else:
                        row['base_price'] = row['price_paid'] - row['paypal_donation_amount']
                        row['nmr'] = 0
                    row['paypal_match'] = paypal_invoice_num
                    row['Gross'] = counts_obj[paypal_invoice_num]['Gross']
                    row['Fee'] = counts_obj[paypal_invoice_num]['Fee']
                    row['Net'] = counts_obj[paypal_invoice_num]['Net']
                    unmatched_invoices.append(row)
        

        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        writer = pd.ExcelWriter(path1, engine='xlsxwriter')
        
        pd.DataFrame(counts).to_excel(writer, sheet_name='Report' ,index = True)
        pd.DataFrame(unmatched_invoices).to_excel(writer, sheet_name='Partial Match' ,index = True)
        pd.DataFrame(errors).to_excel(writer, sheet_name='Errors' ,index = True)
        pd.DataFrame(checks_list).to_excel(writer,sheet_name='Checks',index=True)

        writer.close()
        return send_file(path2)
    
    if report_type == 'log_export':

        file = 'log_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT id, regid, userid, (SELECT username FROM users WHERE users.id = reglogs.userid), timestamp, action FROM reglogs"
        df = pd.read_sql_query(rptquery, engine)

        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)

    if report_type == 'minor_waivers':
        file = 'minor_waivers_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT regid, fname, lname, minor_waiver FROM registrations WHERE minor_waiver IS NOT NULL"
        df = pd.read_sql_query(rptquery, engine)

        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)

    return render_template('reports.html', form=form)
    
@app.route('/waiver', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "Troll Shift Lead", "Troll User",'Department Head')
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
@roles_accepted('Admin', "Troll User", "Troll Shift Lead",'Department Head')
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