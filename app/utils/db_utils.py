from flask_login import current_user
from app.models import *
import os
from werkzeug.exceptions import abort
import psycopg2
import psycopg2.extras
from sqlalchemy import or_, and_
import json
import ast
import pandas as pd
from datetime import datetime, timedelta

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

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def get_reg(regid):
    reg = Registrations.query.filter_by(id=regid).first()
    if reg is None:
        abort(404)
    return reg

def get_regs(regids):
    regs = Registrations.query.filter(Registrations.id.in_(ast.literal_eval(regids))).all()
    if regs is None:
        abort(404)
    return regs

def get_inv(invnumber):
    inv = Invoice.query.filter(Invoice.invoice_number==int(invnumber)).first()
    if inv is None:
        abort(404)
    return inv

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

def get_merchants(regids):
    regs = Merchant.query.filter(Merchant.id.in_(ast.literal_eval(regids))).all()
    if regs is None:
        abort(404)
    return regs

def get_earlyon(regids):
    regs = EarlyOnRequest.query.filter(EarlyOnRequest.id.in_(ast.literal_eval(regids))).all()
    if regs is None:
        abort(404)
    return regs

def get_inspection_stats():
    inspection_stats = {}
    inspections = MarshalInspection.query.all()
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

def get_user(userid):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        abort(404)
    return user

def currentuser_has_permission_on_user(cuser, user):
    if cuser.has_role('Admin'):
        return True
    elif cuser.has_role('Marshal Admin') and user.has_role('Marshal User'):
        return True
    elif (cuser.has_role('Troll Shift Lead') or cuser.has_role('Department Head')) and user.has_role('Troll User'):
        return True
    elif cuser.has_role('Department Head') and user.has_role('Troll Shift Lead'):
        return True
    else:
        return False

def get_role(roleid):
    role = Role.query.filter_by(id=roleid).first()
    if role is None:
        abort(404)
    return role

def get_roles():
    roles = Role.query.all()
    if roles is None:
        abort(404)
    return roles

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

def get_lodging_choices():

    lodgings = Lodging.query.filter().all()
    lodging_choices = [('-', '-')]
    lodging_dict = {}
    for l in lodgings:
        lodging_dict[l.name] = l
        lodging_choices.append([l.id, l.name])
    
    return lodging_choices

def get_kingdom_choices():
    kingdoms = Kingdom.query.all()
    kingdom_choices = [('-', '-')]
    kingdom_dict = {}
    for l in kingdoms:
        kingdom_dict[l.name] = l
        kingdom_choices.append([l.id, l.name])
    
    return kingdom_choices

# def get_event_choices():
#     events = Event.query.all()
#     event_choices = []
#     event_dict = {}
#     if current_user.event_id == None:
#         event_choices.append((0, 'Select Event'))
#     for e in events:
#         event_dict[e.name] = e

#         if current_user.event_id == e.id:
#             event_choices.append([e.id, e.name+" "+str(e.year)])
#         elif current_user.event_id == None:
#             event_choices.append([e.id, e.name+" "+str(e.year)])
    
#     return event_choices

def log_reg_action(reg, action):
    print(reg)
    reglog = RegLogs(
        regid = reg.id,
        userid = current_user.id,
        timestamp = datetime.now(),
        action = action
    )
    db.session.add(reglog)
    db.session.commit()

def calculate_price_calc(reg):
    today_datetime = datetime.today()
    if today_datetime < datetime(2025,3,8).date():
        today_date = datetime(2025,3,8).strftime('%Y-%m-%d')
    elif today_datetime > datetime(2025,3,15).date():
        today_date = datetime(2025,3,15).strftime('%Y-%m-%d')
    else:
        today_date = today_datetime.strftime('%Y-%m-%d')

    with open('rate_sheet.json') as f:
        rate_sheet = json.load(f)
        if reg.age.__contains__('18+'):
            if reg.prereg == True and reg.mbr == 'Member':
                price_calc = rate_sheet['Pre-Registered Member'][today_date]
            elif reg.prereg != True and reg.mbr == 'Member':
                price_calc = rate_sheet['At the Door Member'][today_date]
            elif reg.prereg == True and reg.mbr != 'Member':
                price_calc = rate_sheet['Pre-Registered Non-Member'][today_date]
            elif reg.prereg != True and reg.mbr != 'Member':
                price_calc = rate_sheet['At the Door Non-Member'][today_date]               
        else:
            price_calc = 0

    return price_calc

def get_prereg_pricesheet_day(date):
    pricesheet = PriceSheet.query.filter(PriceSheet.arrival_date == date).first()
    return pricesheet.prereg_price, pricesheet.nmr

def get_atd_pricesheet_day(date):
    pricesheet = PriceSheet.query.filter(PriceSheet.arrival_date == date).first()
    if pricesheet == None:
        return 999, 999
    return pricesheet.atf_price, pricesheet.nmr

def recalculate_reg_balance(reg):
    total_payments = 0
    total_due = reg.registration_price + reg.nmr_price + reg.paypal_donation
    if len(reg.payments) > 0:
        for payment in reg.payments:
            total_payments += payment.amount
        new_balance = total_due - total_payments
    else:
        new_balance = reg.registration_price + reg.nmr_price + reg.paypal_donation
    return new_balance

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

def get_earlyon_arrival_dates():
    returned_dates = []
    event = EventVariables.query.first()
    event_start = event.start_date + timedelta(days=-3)
    event_end = event.start_date
    event_dates = pd.date_range(start=event_start, end=event_end).tolist()
    for date in event_dates:
        date_tup = (date.strftime('%Y-%m-%d'), date.strftime('%A - %B %d, %Y'))
        returned_dates.append(date_tup)
    return returned_dates

def get_reg_arrival_dates():
    returned_dates = []
    event = EventVariables.query.first()
    event_start = event.start_date
    event_end = event.end_date
    event_dates = pd.date_range(start=event_start, end=event_end).tolist()
    for date in event_dates:
        date_tup = (date.strftime('%Y-%m-%d'), date.strftime('%A - %B %d, %Y'))
        returned_dates.append(date_tup)
    return returned_dates

def get_merch_arrival_dates():
    returned_dates = []
    event = EventVariables.query.first()
    event_start = event.start_date + timedelta(days=-1)
    event_end = event.end_date + timedelta(days=-8)
    event_dates = pd.date_range(start=event_start, end=event_end).tolist()
    for date in event_dates:
        date_tup = (date.strftime('%Y-%m-%d'), date.strftime('%A - %B %d, %Y'))
        returned_dates.append(date_tup)
        print(date_tup)
    return returned_dates

def get_department_choices():
    departments = Department.query.all()
    department_choices = [(None, '-')]
    for d in departments:
        department_tup = (d.id, d.name)
        department_choices.append(department_tup)
    return department_choices