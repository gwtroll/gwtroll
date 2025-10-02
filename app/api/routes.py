from app.api import bp
from app.utils.security_utils import *
from flask_login import login_required
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from datetime import datetime
from flask import jsonify
import requests

from flask_security import roles_accepted

def init_data_obj(labels=[]):
    data = {}
    data['labels'] = []
    data['datasets'] = []
    for label in labels:
        data['datasets'].append({'data':[],'label':label})
    return data

@bp.route('/preregistrations', methods=('GET',''))
@login_required
@permission_required('admin')
def preregistrations():
    data = init_data_obj(['Pre-Registrations'])

    results = Registrations.query.filter(Registrations.prereg == True).order_by(Registrations.reg_date_time).all()
    results_counts = {}
    for r in results:
        date = datetime.strftime(r.reg_date_time,'%m/%d/%Y')
        if date not in results_counts:
            results_counts[date] = 1
        else:
            results_counts[date] += 1
    
    for key in results_counts.keys():
        data['labels'].append(key)
        data['datasets'][0]['data'].append(results_counts[key])

    return json.dumps(data)

@bp.route('/checkins', methods=('GET',''))
@login_required
@permission_required('admin')
def checkins():
    data = init_data_obj(['Checkins'])

    results = Registrations.query.all()
    results_counts = {'PreReg Not Checked In':0,'PreReg Checked In':0,'ATD Registration':0}
    for r in results:
        if r.prereg == True:
            if r.checkin is None:
                results_counts['PreReg Not Checked In'] += 1
            else:
                results_counts['PreReg Checked In'] += 1
        else:
            results_counts['ATD Registration'] += 1

    
    for key in results_counts.keys():
        data['labels'].append(key)
        data['datasets'][0]['data'].append(results_counts[key])

    return json.dumps(data)

@bp.route('/registrations/bykingdom', methods=('GET',''))
@login_required
@permission_required('admin')
def registrations_bykingdom():
    data = init_data_obj(['Registrations by Kingdom'])

    results = Registrations.query.filter(Registrations.duplicate==False).all()
    results_counts = {}
    for r in results:
        if r.kingdom.name not in results_counts:
            results_counts[r.kingdom.name] = 1
        else:
            results_counts[r.kingdom.name] += 1
    
    for key in results_counts.keys():
        data['labels'].append(key)
        data['datasets'][0]['data'].append(results_counts[key])

    return json.dumps(data)

@bp.route('/invoice/status_amount', methods=('GET',''))
@login_required
@permission_required('admin')
def invoice_status():
    data = init_data_obj(['Invoice Status Amount'])
# invoice_status
# invoice_total
    results = Invoice.query.filter(Invoice.invoice_status != 'DUPLICATE').all()
    unsent = Registrations.query.filter(Registrations.prereg == True, Registrations.duplicate == False, Registrations.invoice_number == None)
    results_counts = {'UNSENT':0,'OPEN':0,'PAID':0,'NO PAYMENT':0}
    for r in results:
        if r.invoice_status is not None and r.invoice_total is not None:
            results_counts[r.invoice_status] += float(r.invoice_total)
    
    for u in unsent:
        results_counts['UNSENT'] += float(u.total_due)
    
    for key in results_counts.keys():
        data['labels'].append(key)
        data['datasets'][0]['data'].append(results_counts[key])

    return json.dumps(data)

@bp.route('/user/permissions', methods=('GET',''))
@login_required
def user_permissions():
    permissions = current_user.get_permission_set()
    permission_string = json.dumps(permissions)
    return json.loads(permission_string)

@bp.route('/registration/search/<key>/<value>', methods=('GET',''))
@login_required
@permission_required('registration_view')
def search_registration(key,value):

    data = {'prereg_price':0,'regs':[]}
    pricesheet = PriceSheet.query.filter(PriceSheet.arrival_date==datetime.now(pytz.timezone('America/Chicago')).date()).first()
    if pricesheet == None:
        pricesheet = PriceSheet.query.order_by(PriceSheet.arrival_date).first()
    data['prereg_price'] = pricesheet.prereg_price
    if key == 'name':
        regs = Registrations.query.filter(and_(or_(sa.cast(Registrations.fname,sa.Text).ilike('%' + value + '%'),sa.cast(Registrations.lname,sa.Text).ilike('%' + value + '%'),sa.cast(Registrations.scaname,sa.Text).ilike('%' + value + '%'))),Registrations.duplicate==False, or_(Registrations.canceled == False, Registrations.canceled == None)).order_by(Registrations.checkin.desc(),Registrations.lname,Registrations.fname).all()
        # reg = query_db(
        #     "SELECT * FROM registrations WHERE (fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s) AND duplicate = false order by checkin DESC, lname, fname",
        #     #(value, value, value))
        #     ('%' + value + '%', '%' + value + '%', '%' + value + '%'))

    elif key == 'inv':
        regs = Registrations.query.filter(and_(sa.cast(Registrations.invoice_number,sa.Text).ilike('%' + value + '%'),Registrations.duplicate==False, or_(Registrations.canceled == False, Registrations.canceled == None))).order_by(Registrations.checkin.desc(),Registrations.lname,Registrations.fname).all()
        # reg = query_db(
        #     "SELECT * FROM registrations WHERE CAST(invoice_number AS TEXT) ILIKE %s AND duplicate = false order by checkin DESC, lname, fname",
        #     ('%' + value + '%',))

    elif key == 'mbr':
        regs = Registrations.query.filter(and_(sa.cast(Registrations.mbr_num,sa.Text).ilike('%' + value + '%'),Registrations.duplicate==False, or_(Registrations.canceled == False, Registrations.canceled == None))).order_by(Registrations.checkin.desc(),Registrations.lname,Registrations.fname).all()
        # reg = query_db(
        #     "SELECT * FROM registrations WHERE CAST(mbr_num AS TEXT) ILIKE %s AND duplicate = false order by checkin DESC, lname, fname",
        #     ('%' + value + '%',))

    elif key == 'med':
        regs = Registrations.query.filter(sa.cast(Registrations.medallion,sa.Text)==value).order_by(Registrations.checkin.desc(),Registrations.lname,Registrations.fname).all()
        # reg = query_db(
        #     "SELECT * FROM registrations WHERE medallion = %s order by checkin DESC, lname, fname",
        #     (value,))
    
    if regs:
        for reg in regs:
            reg_str = reg.toJSON()
            reg_json = json.loads(reg_str)
            data['regs'].append(json.dumps(reg_json))

    return data

@bp.route('/scheduledevents/<int:scheduledeventid>/add', methods=('','POST'))
@login_required
def addscheduledevent(scheduledeventid):
    scheduledevent = ScheduledEvent.query.get_or_404(int(scheduledeventid))
    if scheduledevent not in current_user.scheduled_events:
        current_user.scheduled_events.append(scheduledevent)
        db.session.commit()
    return jsonify({"message": "Request successful!"}), 200


@bp.route('/scheduledevents/<int:scheduledeventid>/remove', methods=('','POST'))
@login_required
def removescheduledevent(scheduledeventid):
    scheduledevent = ScheduledEvent.query.get_or_404(scheduledeventid)
    if scheduledevent in current_user.scheduled_events:
        current_user.scheduled_events.remove(scheduledevent)
        db.session.commit()
    return jsonify({"message": "Request successful!"}), 200

@bp.route('/paypal/info', methods=('GET',''))
@login_required
@permission_required('admin')
def paypal_info():
    data={
        'url':os.environ.get('PAYPAL_API_BASE_URL'),
        'client':os.environ.get("PAYPAL_CLIENT_ID"),
        'secret':os.environ.get("PAYPAL_SECRET"),
        'webhook':os.environ.get("PAYPAL_PAYMENT_WEBHOOK_ID")
    }
    return data

@bp.route('/paypal/test_auth', methods=('GET',''))
@login_required
@permission_required('admin')
def paypal_auth_test():
    url = f"{os.environ.get('PAYPAL_API_BASE_URL')}/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(
        url, headers=headers, data=data, auth=(os.environ.get("PAYPAL_CLIENT_ID"), os.environ.get("PAYPAL_SECRET"))
    )

    if response.status_code == 200:
        data_dict = response.json()
        access_token = "Bearer " + data_dict["access_token"]
        return access_token
    else:
        return response.json()