from app.api import bp
from app.utils.security_utils import *
from flask_login import login_required
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from datetime import datetime
from flask import jsonify, request
import json
from sqlalchemy import between

from flask_security import roles_accepted


def init_data_obj(labels=[]):
    data = {}
    data["labels"] = []
    data["datasets"] = []
    for label in labels:
        data["datasets"].append({"data": [], "label": label})
    return data


@bp.route("/preregistrations", methods=("GET", ""))
@login_required
@permission_required("admin")
def preregistrations():
    data = init_data_obj(["Pre-Registrations"])

    results = (
        Registrations.query.filter(Registrations.prereg == True)
        .order_by(Registrations.reg_date_time)
        .all()
    )
    results_counts = {}
    for r in results:
        date = datetime.strftime(r.reg_date_time, "%m/%d/%Y")
        if date not in results_counts:
            results_counts[date] = 1
        else:
            results_counts[date] += 1

    for key in results_counts.keys():
        data["labels"].append(key)
        data["datasets"][0]["data"].append(results_counts[key])

    return json.dumps(data)


@bp.route("/checkins", methods=("GET", ""))
@login_required
@permission_required("admin")
def checkins():
    data = init_data_obj(["Checkins"])

    results = Registrations.query.all()
    results_counts = {
        "PreReg Not Checked In": 0,
        "PreReg Checked In": 0,
        "ATD Registration": 0,
    }
    for r in results:
        if r.prereg == True:
            if r.checkin is None:
                results_counts["PreReg Not Checked In"] += 1
            else:
                results_counts["PreReg Checked In"] += 1
        else:
            results_counts["ATD Registration"] += 1

    for key in results_counts.keys():
        data["labels"].append(key)
        data["datasets"][0]["data"].append(results_counts[key])

    return json.dumps(data)


@bp.route("/registrations/bykingdom", methods=("GET", ""))
@login_required
@permission_required("admin")
def registrations_bykingdom():
    data = init_data_obj(["Registrations by Kingdom"])

    results = Registrations.query.filter(Registrations.duplicate == False).all()
    results_counts = {}
    for r in results:
        if r.kingdom.name not in results_counts:
            results_counts[r.kingdom.name] = 1
        else:
            results_counts[r.kingdom.name] += 1

    for key in results_counts.keys():
        data["labels"].append(key)
        data["datasets"][0]["data"].append(results_counts[key])

    return json.dumps(data)


@bp.route("/invoice/status_amount", methods=("GET", ""))
@login_required
@permission_required("admin")
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
        results_counts["UNSENT"] += float(u.total_due)

    for key in results_counts.keys():
        data["labels"].append(key)
        data["datasets"][0]["data"].append(results_counts[key])

    return json.dumps(data)


@bp.route("/user/permissions", methods=("GET", ""))
@login_required
def user_permissions():
    permissions = current_user.get_permission_set()
    permission_string = json.dumps(permissions)
    return json.loads(permission_string)


@bp.route("/registration/search/<key>/<value>", methods=("GET", ""))
@login_required
@permission_required("registration_view")
def search_registration(key, value):

    data = {"prereg_price": 0, "regs": []}
    pricesheet = PriceSheet.query.filter(
        PriceSheet.arrival_date == datetime.now(pytz.timezone("America/Chicago")).date()
    ).first()
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

    elif key == "med":
        regs = (
            Registrations.query.filter(
                sa.cast(Registrations.medallion, sa.Text) == value
            )
            .order_by(
                Registrations.checkin.desc(), Registrations.lname, Registrations.fname
            )
            .all()
        )

    if regs:
        for reg in regs:
            reg_str = reg.toJSON()
            reg_json = json.loads(reg_str)
            data["regs"].append(json.dumps(reg_json))

    return data


@bp.route("/scheduledevents/<int:scheduledeventid>/add", methods=("", "POST"))
@login_required
def addscheduledevent(scheduledeventid):
    scheduledevent = ScheduledEvent.query.get_or_404(int(scheduledeventid))
    if scheduledevent not in current_user.scheduled_events:
        current_user.scheduled_events.append(scheduledevent)
        db.session.commit()
    return jsonify({"message": "Request successful!"}), 200


@bp.route("/scheduledevents/<int:scheduledeventid>/remove", methods=("", "POST"))
@login_required
def removescheduledevent(scheduledeventid):
    scheduledevent = ScheduledEvent.query.get_or_404(scheduledeventid)
    if scheduledevent in current_user.scheduled_events:
        current_user.scheduled_events.remove(scheduledevent)
        db.session.commit()
    return jsonify({"message": "Request successful!"}), 200

@bp.route("/full_export", methods=("GET", ""))
@login_required
def fullexport():
    data = {}
    columns = [{"field": "id", "title": "ID", "filterControl": 'input'},
        {"field": "fname", "title": "First Name", "filterControl":"input"},
        {"field": "lname", "title": "Last Name", "filterControl":"input"},
        {"field": "scaname", "title": "SCA Name", "filterControl":"input"},
        {"field": "city", "title": "City", "filterControl":"input"},
        {"field": "state_province", "title": "State/Province", "filterControl":"input"},
        {"field": "zip", "title": "Zip", "filterControl":"input"},
        {"field": "country", "title": "Country", "filterControl":"input"},
        {"field": "phone", "title": "Phone", "filterControl":"input"},
        {"field": "email", "title": "Email", "filterControl":"input"},
        {"field": "invoice_email", "title": "Invoice Email", "filterControl":"input"},
        {"field": "age", "title": "Age", "filterControl":"select"},
        {"field": "emergency_contact_name", "title": "Emergenct Contact Name", "filterControl":"input"},
        {"field": "emergency_contact_phone", "title": "Emergenct Contact Phone", "filterControl":"input"},
        {"field": "royal_departure_date", "title": "Royal Departure Date", "filterControl":"select"},
        {"field": "royal_title", "title": "Royal Title", "filterControl":"input"},
        {"field": "mbr", "title": "Membership", "filterControl":"select"},
        {"field": "mbr_num", "title": "Membership Number", "filterControl":"input"},
        {"field": "mbr_num_exp", "title": "Membership Expiration", "filterControl":"input"},
        {"field": "reg_date_time", "title": "Registration Date/Time", "filterControl":"input"},
        {"field": "prereg", "title": "Pre-Registered", "filterControl":"select"},
        {"field": "expected_arrival_date", "title": "Expected Arrival Date", "filterControl":"select"},
        {"field": "early_on_approved", "title": "EarlyOn Approved", "filterControl":"select"},
        {"field": "notes", "title": "Notes"},
        {"field": "duplicate", "title": "Duplicate", "filterControl":"select"},
        {"field": "registration_price", "title": "Registration Price", "filterControl":"select"},
        {"field": "registration_balance", "title": "Registration Balance", "filterControl":"input"},
        {"field": "nmr_price", "title": "NMR Price", "filterControl":"select"},
        {"field": "nmr_balance", "title": "NMR Balance", "filterControl":"input"},
        {"field": "paypal_donation", "title": "PayPal Donation", "filterControl":"input"},
        {"field": "paypal_donation_balance", "title": "PayPal Donation Balance", "filterControl":"input"},
        {"field": "nmr_donation", "title": "NMR Donation", "filterControl":"select"},
        {"field": "total_due", "title": "Total Price", "filterControl":"input"},
        {"field": "balance", "title": "Balance", "filterControl":"input"},
        {"field": "minor_waiver", "title": "Minor Waiver", "filterControl":"input"},
        {"field": "checkin", "title": "Checkin Date/Time", "filterControl":"input"},
        {"field": "medallion", "title": "Medallion", "filterControl":"input"},
        {"field": "actual_arrival_date", "title": "Actual Arrival Date", "filterControl":"input"},
    ]
    rows = []
    full = Registrations.query.filter().all()
    for reg in full:
        reg_json = json.loads(reg.toJSON())
        rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

@bp.route("/full_checkin_report", methods=("GET", ""))
@login_required
def fullcheckinreport():
    dt_start = request.args.get('dt_start')
    dt_end = request.args.get('dt_end')

    print(dt_start)
    print(dt_end)

    data = {}
    columns = [{"field": "id", "title": "ID", "filterControl": 'input'},
        {"field": "fname", "title": "First Name", "filterControl":"input"},
        {"field": "lname", "title": "Last Name", "filterControl":"input"},
        {"field": "scaname", "title": "SCA Name", "filterControl":"input"},
        {"field": "city", "title": "City", "filterControl":"input"},
        {"field": "state_province", "title": "State/Province", "filterControl":"input"},
        {"field": "zip", "title": "Zip", "filterControl":"input"},
        {"field": "country", "title": "Country", "filterControl":"input"},
        {"field": "phone", "title": "Phone", "filterControl":"input"},
        {"field": "email", "title": "Email", "filterControl":"input"},
        {"field": "invoice_email", "title": "Invoice Email", "filterControl":"input"},
        {"field": "age", "title": "Age", "filterControl":"select"},
        {"field": "emergency_contact_name", "title": "Emergenct Contact Name", "filterControl":"input"},
        {"field": "emergency_contact_phone", "title": "Emergenct Contact Phone", "filterControl":"input"},
        {"field": "royal_departure_date", "title": "Royal Departure Date", "filterControl":"select"},
        {"field": "royal_title", "title": "Royal Title", "filterControl":"input"},
        {"field": "mbr", "title": "Membership", "filterControl":"select"},
        {"field": "mbr_num", "title": "Membership Number", "filterControl":"input"},
        {"field": "mbr_num_exp", "title": "Membership Expiration", "filterControl":"input"},
        {"field": "reg_date_time", "title": "Registration Date/Time", "filterControl":"input"},
        {"field": "prereg", "title": "Pre-Registered", "filterControl":"select"},
        {"field": "expected_arrival_date", "title": "Expected Arrival Date", "filterControl":"select"},
        {"field": "early_on_approved", "title": "EarlyOn Approved", "filterControl":"select"},
        {"field": "notes", "title": "Notes"},
        {"field": "duplicate", "title": "Duplicate", "filterControl":"select"},
        {"field": "canceled", "title": "Canceled", "filterControl":"select"},
        {"field": "registration_price", "title": "Registration Price", "filterControl":"select"},
        {"field": "registration_balance", "title": "Registration Balance", "filterControl":"input"},
        {"field": "nmr_price", "title": "NMR Price", "filterControl":"select"},
        {"field": "nmr_balance", "title": "NMR Balance", "filterControl":"input"},
        {"field": "paypal_donation", "title": "PayPal Donation", "filterControl":"input"},
        {"field": "paypal_donation_balance", "title": "PayPal Donation Balance", "filterControl":"input"},
        {"field": "nmr_donation", "title": "NMR Donation", "filterControl":"select"},
        {"field": "total_due", "title": "Total Price", "filterControl":"input"},
        {"field": "balance", "title": "Balance", "filterControl":"input"},
        {"field": "minor_waiver", "title": "Minor Waiver", "filterControl":"input"},
        {"field": "checkin", "title": "Checkin Date/Time", "filterControl":"input"},
        {"field": "medallion", "title": "Medallion", "filterControl":"input"},
        {"field": "actual_arrival_date", "title": "Actual Arrival Date", "filterControl":"input"},
    ]
    rows = []
    all_checkins = Registrations.query.filter(Registrations.checkin != None).order_by(Registrations.id).all()
    for reg in all_checkins:
        reg_json = json.loads(reg.toJSON())
        rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

@bp.route("/at_door_count", methods=("GET", ""))
@login_required
def at_door_count():
    dt_start = request.args.get('dt_start')
    dt_end = request.args.get('dt_end')
    data = {}
    columns = [{"field": "atd", "title": "At the Door", "filterControl": 'input'},
        {"field": "prereg", "title": "Pre-Reg", "filterControl":"input"},
        {"field": "income", "title": "Income Total", "filterControl":"input"},
    ]
    rows = []
    regs = Registrations.query.filter(Registrations.checkin.between(datetime.strptime(dt_start,'%Y-%m-%d'), datetime.strptime(dt_end,'%Y-%m-%d')+timedelta(days=1))).all()
    atd_count = 0
    prereg_count = 0
    income_total = 0
    for reg in regs:
        if reg.prereg is True:
            prereg_count+=1
        else:
            atd_count+=1
        income_total+=reg.total_due
    reg_json = {"atd":atd_count,"prereg":prereg_count,"income":income_total}
    rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

@bp.route("/kingdom_count", methods=("GET", ""))
@login_required
def kingdom_count():
    data = {'columns':[],'rows':[]}
    columns = [{"field": "kingdom", "title": "Kingdom", "filterControl": 'select'}]
    results = Registrations.query.filter(Registrations.checkin != None).order_by(Registrations.checkin).all()
    kingdoms = Kingdom.query.order_by(Kingdom.name).all()
    results_counts = {}
    for k in kingdoms:
        results_counts[k.name] = {}
    dates = []
    for r in results:
        checkin_date = r.checkin.strftime('%m/%d/%Y')
        if checkin_date not in dates:
            dates.append(checkin_date)
            columns.append({"field": checkin_date, "title": checkin_date})
        if checkin_date not in results_counts[r.kingdom.name]:
            results_counts[r.kingdom.name][checkin_date] = 1
        else:
            results_counts[r.kingdom.name][checkin_date] += 1
    
    for i in results_counts:
        temp = {'kingdom':i}
        for d in dates:
            if d in results_counts[i]:
                temp[d]=results_counts[i][d]
            else:
                temp[d]=0
        data['rows'].append(temp)
    data['columns']=columns
    reg_json = json.loads(json.dumps(data))
    return reg_json

@bp.route("/early_on_report", methods=("GET", ""))
@login_required
def earlyon():
    data = {}
    columns = [{"field": "id", "title": "ID", "filterControl": 'input'},
        {"field": "fname", "title": "First Name", "filterControl":"input"},
        {"field": "lname", "title": "Last Name", "filterControl":"input"},
        {"field": "scaname", "title": "SCA Name", "filterControl":"input"},
        {"field": "phone", "title": "Phone", "filterControl":"input"},
        {"field": "email", "title": "Email", "filterControl":"input"},
        {"field": "kingdom", "title": "Kingdom", "filterControl":"select"},
        {"field": "lodging", "title": "Lodging", "filterControl":"select"},
    ]
    rows = []
    earlyon_list = Registrations.query.filter(Registrations.early_on_approved == True, Registrations.balance <= 0).all()
    for reg in earlyon_list:
        kingdom = reg.kingdom.name
        lodging = reg.lodging.name
        reg_json = json.loads(reg.toJSON())
        reg_json['kingdom'] = kingdom
        reg_json['lodging'] = lodging
        rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)


@bp.route("/ghost_report", methods=("GET", ""))
@login_required
def ghost_report():
    data = {}
    columns = [{"field": "invoice_number", "title": "Invoice Number", "filterControl": 'input'},
        {"field": "invoice_status", "title": "Invoice Status", "filterControl": 'select'},      
        {"field": "id", "title": "ID", "filterControl": 'input'},
        {"field": "fname", "title": "First Name", "filterControl":"input"},
        {"field": "lname", "title": "Last Name", "filterControl":"input"},
        {"field": "scaname", "title": "SCA Name", "filterControl":"input"},
        {"field": "age", "title": "Age", "filterControl":"input"},
        {"field": "phone", "title": "Phone", "filterControl":"input"},
        {"field": "email", "title": "Email", "filterControl":"input"},
        {"field": "kingdom", "title": "Kingdom", "filterControl":"select"},
        {"field": "lodging", "title": "Lodging", "filterControl":"select"},
    ]
    rows = []
    ghosts = Registrations.query.filter(Registrations.prereg == True, Registrations.checkin == None, Registrations.invoices != None).order_by(Registrations.lodging_id).all()
    for reg in ghosts:
        invoice_number = reg.invoices[0].invoice_number
        invoice_status = reg.invoices[0].invoice_status
        kingdom = reg.kingdom.name
        lodging = reg.lodging.name
        reg_json = json.loads(reg.toJSON())
        reg_json['kingdom'] = kingdom
        reg_json['lodging'] = lodging
        reg_json['invoice_number'] = invoice_number
        reg_json['invoice_status'] = invoice_status
        rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

@bp.route("/royal_registrations", methods=("GET", ""))
@login_required
def royal_registrations():
    data = {}
    columns = [{"field": "id", "title": "ID", "filterControl": 'input'},
        {"field": "fname", "title": "First Name", "filterControl":"input"},
        {"field": "lname", "title": "Last Name", "filterControl":"input"},
        {"field": "scaname", "title": "SCA Name", "filterControl":"input"},
        {"field": "city", "title": "City", "filterControl":"input"},
        {"field": "state_province", "title": "State/Province", "filterControl":"input"},
        {"field": "zip", "title": "Zip", "filterControl":"input"},
        {"field": "country", "title": "Country", "filterControl":"input"},
        {"field": "phone", "title": "Phone", "filterControl":"input"},
        {"field": "email", "title": "Email", "filterControl":"input"},
        {"field": "invoice_email", "title": "Invoice Email", "filterControl":"input"},
        {"field": "age", "title": "Age", "filterControl":"select"},
        {"field": "emergency_contact_name", "title": "Emergenct Contact Name", "filterControl":"input"},
        {"field": "emergency_contact_phone", "title": "Emergenct Contact Phone", "filterControl":"input"},
        {"field": "royal_departure_date", "title": "Royal Departure Date", "filterControl":"select"},
        {"field": "royal_title", "title": "Royal Title", "filterControl":"input"},
        {"field": "mbr", "title": "Membership", "filterControl":"select"},
        {"field": "mbr_num", "title": "Membership Number", "filterControl":"input"},
        {"field": "mbr_num_exp", "title": "Membership Expiration", "filterControl":"input"},
        {"field": "reg_date_time", "title": "Registration Date/Time", "filterControl":"input"},
        {"field": "prereg", "title": "Pre-Registered", "filterControl":"select"},
        {"field": "expected_arrival_date", "title": "Expected Arrival Date", "filterControl":"select"},
        {"field": "early_on_approved", "title": "EarlyOn Approved", "filterControl":"select"},
        {"field": "notes", "title": "Notes"},
        {"field": "duplicate", "title": "Duplicate", "filterControl":"select"},
        {"field": "registration_price", "title": "Registration Price", "filterControl":"select"},
        {"field": "registration_balance", "title": "Registration Balance", "filterControl":"input"},
        {"field": "nmr_price", "title": "NMR Price", "filterControl":"select"},
        {"field": "nmr_balance", "title": "NMR Balance", "filterControl":"input"},
        {"field": "paypal_donation", "title": "PayPal Donation", "filterControl":"input"},
        {"field": "paypal_donation_balance", "title": "PayPal Donation Balance", "filterControl":"input"},
        {"field": "nmr_donation", "title": "NMR Donation", "filterControl":"select"},
        {"field": "total_due", "title": "Total Price", "filterControl":"input"},
        {"field": "balance", "title": "Balance", "filterControl":"input"},
        {"field": "minor_waiver", "title": "Minor Waiver", "filterControl":"input"},
        {"field": "checkin", "title": "Checkin Date/Time", "filterControl":"input"},
        {"field": "medallion", "title": "Medallion", "filterControl":"input"},
        {"field": "actual_arrival_date", "title": "Actual Arrival Date", "filterControl":"input"},
    ]
    rows = []
    royals = Registrations.query.filter(Registrations.age=='Royals').order_by(Registrations.id).all()
    for reg in royals:
        kingdom = reg.kingdom.name
        lodging = reg.lodging.name
        reg_json = json.loads(reg.toJSON())
        reg_json['kingdom'] = kingdom
        reg_json['lodging'] = lodging
        rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)