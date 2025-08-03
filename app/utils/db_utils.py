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

lodging_cache_time = datetime.now()
lodging_choices = None

kingdom_cache_time = datetime.now()
kingdom_choices = None

pre_reg_pricesheet_cache_time = datetime.now()
pre_reg_pricesheet = None

atd_reg_pricesheet_cache_time = datetime.now()
atd_reg_pricesheet = None

checkin_count_cache_time = datetime.now()
checkin_count = None

topic_cache_time = datetime.now()
topic_choices = None

tag_cache_time = datetime.now()
tag_choices = None

scheduledevents_cache_time = datetime.now()
scheduledevents_cache = None

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

# def query_db(query, args=(), one=False):
#     conn = get_db_connection()
#     cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
#     cur.execute(query, args)
#     rv = cur.fetchall()
#     conn.close()
#     return (rv[0] if rv else None) if one else rv

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
    global checkin_count_cache_time
    global checkin_count
    if checkin_count != None and checkin_count_cache_time > datetime.now() + timedelta(minutes=-10):
        return checkin_count
    else:
        count = len(Registrations.query.with_entities(Registrations.id).filter(Registrations.checkin is not None).all())
        checkin_count = count
        checkin_count_cache_time = datetime.now()
        return checkin_count

# def reg_count():
#     conn= get_db_connection()
#     cur = conn.cursor()
#     cur.execute('SELECT count(*) FROM registrations WHERE checkin IS NOT NULL;', [])
#     results = cur.fetchone()
#     for regcount in results:
#         print(regcount)
#     conn.close()
#     if regcount is None:
#         abort(404)
#     return regcount

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
    roles = Role.query.order_by(Role.name).all()
    if roles is None:
        abort(404)
    return roles

def get_role_choices():
    roles = get_roles()
    role_choices = []
    role_dict = {}
    for r in roles:
        role_dict[r.name] = r

    if current_user.has_permission('admin'):
        for r in roles:
            role_choices.append([r.id, r.name])
        return role_choices
    
    if current_user.has_role('Marshal Admin'):
        role_choices.append([role_dict['Marshal User'].id,'Marshal User'])

    if current_user.has_role('Troll Shift Lead') or current_user.has_role('Head Troll'):
        role_choices.append([role_dict['Troll User'].id,'Troll User'])
    
    if current_user.has_role('Head Troll'):
        role_choices.append([role_dict['Troll Shift Lead'].id,'Troll Shift Lead'])

    return role_choices

def get_permission(permissionid):
    permission = Permissions.query.filter_by(id=permissionid).first()
    if permission is None:
        abort(404)
    return permission

def get_permission_choices():
    permissions = Permissions.query.order_by(Permissions.name).all()
    permission_choices = []
    permission_dict = {}
    for p in permissions:
        permission_dict[p.name] = p
        permission_choices.append([p.id, p.name])
    
    return permission_choices

def get_lodging_choices():
    global lodging_cache_time
    global lodging_choices
    if lodging_choices != None and lodging_cache_time > datetime.now() + timedelta(hours=-1):
        return lodging_choices
    else:
        lodgings = Lodging.query.order_by(Lodging.name).all()
        local_lodging_choices = [('-', '-')]
        for l in lodgings:
            local_lodging_choices.append([l.id, l.name])
        lodging_choices = local_lodging_choices
        lodging_cache_time = datetime.now()
        return lodging_choices

def get_kingdom_choices():
    global kindgom_cache_time
    global kingdom_choices
    if kingdom_choices != None and kindgom_cache_time > datetime.now() + timedelta(hours=-1):
        return kingdom_choices
    else:
        kingdoms = Kingdom.query.order_by(Kingdom.name).all()
        local_kingdom_choices = [('-', '-')]
        for l in kingdoms:
            local_kingdom_choices.append([l.id, l.name])
        kingdom_choices = local_kingdom_choices
        kindgom_cache_time = datetime.now()
        return kingdom_choices

def get_topic_choices():
    global topic_cache_time
    global topic_choices
    if topic_choices != None and topic_cache_time > datetime.now() + timedelta(hours=-1):
        return topic_choices
    else:
        topics = Topic.query.order_by(Topic.name).all()
        local_topic_choices = [('-', '-')]
        for t in topics:
            local_topic_choices.append([t.id, t.name])
        topic_choices = local_topic_choices
        topic_cache_time = datetime.now()
        return topic_choices
    
def get_tag(tagid):
    tag = Tag.query.filter(Tag.id==tagid).first()
    return tag

def get_tags(tagids):
    tags = Tag.query.filter(Tag.id.id.in_(ast.literal_eval(tagids))).all()
    return tags

def get_tag_choices():
    global tag_cache_time
    global tag_choices
    if tag_choices != None and tag_cache_time > datetime.now() + timedelta(hours=-1):
        return tag_choices
    else:
        tags = Tag.query.order_by(Tag.name).all()
        local_tag_choices = [('-', '-')]
        for t in tags:
            local_tag_choices.append([t.id, t.name])
        tag_choices = local_tag_choices
        tag_cache_time = datetime.now()
        return tag_choices
    
def get_user_instructor_choices():
    local_user_instructors_choices = []
    user_instructors = User.query.join(UserRoles, UserRoles.user_id==User.id).join(Role, Role.id==UserRoles.role_id).filter(Role.name=='Teacher').order_by(User.fname).all()
    local_user_instructors_choices = [('-', '-')]
    for u in user_instructors:
        local_user_instructors_choices.append([u.id, u.fname + ' ' + u.lname])
    return local_user_instructors_choices

def get_scheduledevents():
    global scheduledevents_cache_time
    global scheduledevents_cache
    if scheduledevents_cache != None and scheduledevents_cache_time > datetime.now() + timedelta(hours=-1):
        return scheduledevents_cache
    else:
        scheduledevents = ScheduledEvent.query.order_by(ScheduledEvent.start_datetime, ScheduledEvent.name).all()
        scheduledevents_cache = scheduledevents
        scheduledevents_cache_time = datetime.now()
        return scheduledevents_cache

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

# def log_reg_action(reg, action):
#     print(reg)
#     reglog = RegLogs(
#         regid = reg.id,
#         userid = current_user.id,
#         timestamp = datetime.now(),
#         action = action
#     )
#     db.session.add(reglog)
#     db.session.commit()

# def calculate_price_calc(reg):
#     today_datetime = datetime.today()
#     if today_datetime < datetime(2025,3,8).date():
#         today_date = datetime(2025,3,8).strftime('%Y-%m-%d')
#     elif today_datetime > datetime(2025,3,15).date():
#         today_date = datetime(2025,3,15).strftime('%Y-%m-%d')
#     else:
#         today_date = today_datetime.strftime('%Y-%m-%d')

#     with open('rate_sheet.json') as f:
#         rate_sheet = json.load(f)
#         if reg.age.__contains__('18+'):
#             if reg.prereg == True and reg.mbr == 'Member':
#                 price_calc = rate_sheet['Pre-Registered Member'][today_date]
#             elif reg.prereg != True and reg.mbr == 'Member':
#                 price_calc = rate_sheet['At the Door Member'][today_date]
#             elif reg.prereg == True and reg.mbr != 'Member':
#                 price_calc = rate_sheet['Pre-Registered Non-Member'][today_date]
#             elif reg.prereg != True and reg.mbr != 'Member':
#                 price_calc = rate_sheet['At the Door Non-Member'][today_date]               
#         else:
#             price_calc = 0

#     return price_calc

def get_prereg_pricesheet_day(date):
    global pre_reg_pricesheet_cache_time
    global pre_reg_pricesheet
    if pre_reg_pricesheet != None and pre_reg_pricesheet_cache_time > datetime.now() + timedelta(hours=-1):
        if date in pre_reg_pricesheet:
            return pre_reg_pricesheet[date]
        else:
            return get_prereg_pricesheet_day_not_in_sheet()
    else:
        pricesheet = PriceSheet.query.all()
        prices = {}
        for price in pricesheet:
            prices[price.arrival_date.strftime("%Y/%m/%d")] = price.prereg_price
        pre_reg_pricesheet = prices
        if date in pre_reg_pricesheet:
            return pre_reg_pricesheet[date]
        else:
            return get_prereg_pricesheet_day_not_in_sheet()

def get_prereg_pricesheet_day_not_in_sheet():
    pricesheet = PriceSheet.query.order_by(PriceSheet.arrival_date).first()
    return pricesheet.prereg_price

def get_atd_pricesheet_day(date):
    global atd_reg_pricesheet_cache_time
    global atd_reg_pricesheet
    if atd_reg_pricesheet != None and atd_reg_pricesheet_cache_time > datetime.now() + timedelta(hours=-1):
        if date.strftime("%Y/%m/%d") in atd_reg_pricesheet:
            return atd_reg_pricesheet[date.strftime("%Y/%m/%d")]
        else:
            return get_atd_pricesheet_day_not_in_sheet()
    else:
        pricesheet = PriceSheet.query.all()
        prices = {}
        for price in pricesheet:
            prices[price.arrival_date.strftime("%Y/%m/%d")] = price.atd_price
        atd_reg_pricesheet = prices
        if date.strftime("%Y/%m/%d") in atd_reg_pricesheet:
            return atd_reg_pricesheet[date.strftime("%Y/%m/%d")]
        else:
            return get_atd_pricesheet_day_not_in_sheet()
    
def get_atd_pricesheet_day_not_in_sheet():
    pricesheet = PriceSheet.query.order_by(PriceSheet.arrival_date).first()
    return pricesheet.atd_price

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

def inv_prereg_unsent_counts():
    return {'Prereg':prereg_total(),'Regs':unsent_reg_count(),'Inv':unsent_count()}

def prereg_total():
    regs = Registrations.query.with_entities(Registrations.id).filter(and_(Registrations.duplicate==False, Registrations.prereg==True)).all()
    return len(regs)

def unsent_count():
    unsent=0
    unsent_reg = Registrations.query.with_entities(Registrations.invoice_email).filter(and_(Registrations.invoices == None, Registrations.prereg == True, Registrations.duplicate == False, Registrations.balance > 0)).distinct(Registrations.invoice_email).all()
    unsent += len(unsent_reg)
    unsent_merch = Merchant.query.with_entities(Merchant.id).filter(and_(Merchant.invoice_number == None, Merchant.status == "APPROVED")).all()
    unsent += len(unsent_merch)
    unsent_earlyon = EarlyOnRequest.query.with_entities(EarlyOnRequest.id).filter(and_(EarlyOnRequest.invoice_number == None, EarlyOnRequest.rider_balance > 0, EarlyOnRequest.dept_approval_status == 'APPROVED', EarlyOnRequest.autocrat_approval_status == 'APPROVED')).all()
    unsent += len(unsent_earlyon)
    return unsent

def unsent_reg_count():
    unsent_reg = Registrations.query.with_entities(Registrations.id).filter(and_(Registrations.invoices == None, Registrations.prereg == True, Registrations.duplicate == False, Registrations.balance > 0)).all()
    return len(unsent_reg)

def inv_prereg_open_counts():
    return {'Prereg':prereg_total(),'Regs':open_reg_count(),'Inv':open_count()}

def open_count():
    open_inv = Invoice.query.with_entities(Invoice.invoice_number).filter(Invoice.invoice_status=='OPEN').all()
    return len(open_inv)

def open_reg_count():
    count = 0
    open_reg = Invoice.query.filter(and_(Invoice.invoice_status=='OPEN')).all()
    for inv in open_reg:
        for reg in inv.regs:
            if reg.duplicate == False: 
                count+=1
    return count

def inv_prereg_paid_counts():
    return {'Prereg':prereg_total(),'Regs':paid_reg_count(),'Inv':paid_count()}

def paid_count():
    open_inv = Invoice.query.with_entities(Invoice.invoice_number).filter(Invoice.invoice_status=='PAID').all()
    return len(open_inv)

def paid_reg_count():
    count = 0
    paid_reg = Invoice.query.filter(and_(Invoice.invoice_status=='PAID')).all()
    for inv in paid_reg:
        for reg in inv.regs:
            if reg.duplicate == False: 
                count+=1
    return count

def inv_prereg_canceled_counts():
    return {'Prereg':prereg_total(),'Regs':canceled_reg_count(),'Inv':canceled_count()}

def canceled_count():
    canceled_inv = Invoice.query.with_entities(Invoice.invoice_number).filter(or_(Invoice.invoice_status=='NO PAYMNET', Invoice.invoice_status=='DUPLICATE')).all()
    return len(canceled_inv)

def canceled_reg_count():
    count = 0
    canceled_reg = Invoice.query.filter(or_(Invoice.invoice_status=='NO PAYMNET', Invoice.invoice_status=='DUPLICATE')).all()
    for inv in canceled_reg:
        for reg in inv.regs:
            if reg.duplicate == False: 
                count+=1
    return count

def inv_prereg_all_counts():
    return {'Prereg':prereg_total(),'Regs':all_reg_count(),'Inv':all_count()}

def all_count():
    invs = Invoice.query.with_entities(Invoice.invoice_number).filter(and_(Invoice.invoice_status!='NO PAYMNET', Invoice.invoice_status!='DUPLICATE')).all()
    return len(invs)

def all_reg_count():
    count = 0
    regs = Invoice.query.filter(and_(Invoice.invoice_status!='NO PAYMNET', Invoice.invoice_status!='DUPLICATE')).all()
    for inv in regs:
        for reg in inv.regs:
            if reg.duplicate == False: 
                count+=1
    return count

def get_earlyon_arrival_dates():
    returned_dates = [('-','-')]
    event = EventVariables.query.first()
    event_start = event.start_date + timedelta(days=-3)
    event_end = event.start_date
    event_dates = pd.date_range(start=event_start, end=event_end).tolist()
    for date in event_dates:
        date_tup = (date.strftime('%Y/%m/%d'), date.strftime('%A - %B %d, %Y'))
        returned_dates.append(date_tup)
    return returned_dates

def get_reg_arrival_dates():
    returned_dates = [('-','-')]
    event = EventVariables.query.first()
    event_start = event.start_date
    event_end = event.end_date + timedelta(days=-1)
    event_dates = pd.date_range(start=event_start, end=event_end).tolist()
    for date in event_dates:
        date_tup = (date.strftime('%Y/%m/%d'), date.strftime('%A - %B %d, %Y'))
        returned_dates.append(date_tup)
    return returned_dates

def get_merch_arrival_dates():
    returned_dates = [('-','-')]
    event = EventVariables.query.first()
    event_start = event.start_date + timedelta(days=-1)
    event_end = event.end_date + timedelta(days=-8)
    event_dates = pd.date_range(start=event_start, end=event_end).tolist()
    for date in event_dates:
        date_tup = (date.strftime('%Y/%m/%d'), date.strftime('%A - %B %d, %Y'))
        returned_dates.append(date_tup)
    return returned_dates

def get_department_choices():
    departments = Department.query.order_by(Department.name).all()
    department_choices = [(None, '-')]
    for d in departments:
        department_tup = (d.id, d.name)
        department_choices.append(department_tup)
    return department_choices