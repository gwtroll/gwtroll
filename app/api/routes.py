from app.api import bp
from app.utils.security_utils import *
from flask_login import login_required
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from datetime import datetime
from flask import jsonify, request
import json
import copy
from app.utils.paypal_api import get_paypal_invoices, get_paypal_payment, get_paypal_transactions

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

    results = Registrations.query.filter(Registrations.duplicate != True, Registrations.canceled != True).all()
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
    unsent = Registrations.query.filter(Registrations.prereg == True, Registrations.duplicate != True, Registrations.canceled != True, Registrations.invoice_number == None)
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
        regs = Registrations.query.filter(and_(or_(sa.cast(Registrations.fname,sa.Text).ilike('%' + value + '%'),sa.cast(Registrations.lname,sa.Text).ilike('%' + value + '%'),sa.cast(Registrations.scaname,sa.Text).ilike('%' + value + '%'))),Registrations.duplicate!=True, Registrations.canceled != True).order_by(Registrations.checkin.desc(),Registrations.lname,Registrations.fname).all()
        # reg = query_db(
        #     "SELECT * FROM registrations WHERE (fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s) AND duplicate = false order by checkin DESC, lname, fname",
        #     #(value, value, value))
        #     ('%' + value + '%', '%' + value + '%', '%' + value + '%'))

    elif key == 'inv':
        regs = Registrations.query.filter(and_(sa.cast(Registrations.invoice_number,sa.Text).ilike('%' + value + '%'),Registrations.duplicate!=True, Registrations.canceled != True)).order_by(Registrations.checkin.desc(),Registrations.lname,Registrations.fname).all()
        # reg = query_db(
        #     "SELECT * FROM registrations WHERE CAST(invoice_number AS TEXT) ILIKE %s AND duplicate = false order by checkin DESC, lname, fname",
        #     ('%' + value + '%',))

    elif key == 'mbr':
        regs = Registrations.query.filter(and_(sa.cast(Registrations.mbr_num,sa.Text).ilike('%' + value + '%'),Registrations.duplicate!=True, Registrations.canceled != True)).order_by(Registrations.checkin.desc(),Registrations.lname,Registrations.fname).all()
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
@permission_required('registration_reports')
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
    full = Registrations.query.filter().all()
    for reg in full:
        reg_json = json.loads(reg.toJSON())
        rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

@bp.route("/full_checkin_report", methods=("GET", ""))
@login_required
@permission_required('registration_reports')
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
@permission_required('registration_reports')
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
@permission_required('registration_reports')
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
@permission_required('registration_reports')
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
@permission_required('registration_reports')
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
@permission_required('registration_reports')
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

@bp.route("/merchant_full_export", methods=("GET", ""))
@login_required
@permission_required('merchant_reports')
def merchant_fullexport():
    data = {}

    # {"field": "", "title": "", "filterControl":"input"}
    # invoice_number = db.Column(db.Integer(), db.ForeignKey("invoice.invoice_number"))
    # {"field": "", "title": "", "filterControl":"input"}
    # invoice = db.relationship("Invoice", back_populates="merchants")
    # {"field": "", "title": "", "filterControl":"input"}
    # payments = db.relationship("Payment", back_populates="merchant")
    # {"field": "", "title": "", "filterControl":"input"}

    columns = [{"field": "id", "title": "ID", "filterControl": 'input'},
    {"field": "status", "title": "Status", "filterControl": 'select'},
    {"field": "business_name", "title": "Business Name", "filterControl": 'input'},
    {"field": "sca_name", "title": "SCA Name", "filterControl": 'input'},
    {"field": "fname", "title": "First Name", "filterControl":"input"},
    {"field": "lname", "title": "Last Name", "filterControl":"input"},
    {"field": "email", "title": "Email", "filterControl":"input"},
    {"field": "phone", "title": "Phone", "filterControl":"input"},
    {"field": "text_permission", "title": "Text Permission", "filterControl":"select"},
    {"field": "address", "title": "Address", "filterControl":"input"},
    {"field": "city", "title": "City", "filterControl":"input"},
    {"field": "state_province", "title": "State/Province", "filterControl":"input"},
    {"field": "zip", "title": "Zip", "filterControl":"input"},
    {"field": "frontage_width", "title": "Frontage Width", "filterControl":"input"},
    {"field": "frontage_depth", "title": "Frontage Depth", "filterControl":"input"},
    {"field": "ropes_front", "title": "Ropes Front", "filterControl":"input"},
    {"field": "ropes_back", "title": "Ropes Back", "filterControl":"input"},
    {"field": "ropes_left", "title": "Ropes Left", "filterControl":"input"},
    {"field": "ropes_right", "title": "Ropes Right", "filterControl":"input"},
    {"field": "space_fee", "title": "Space Fee", "filterControl":"input"},
    {"field": "space_fee_balance", "title": "Space Fee Balance", "filterControl":"input"},
    {"field": "additional_space_information", "title": "Additional Space Information", "filterControl":"input"},
    {"field": "processing_fee", "title": "Processing Fee", "filterControl":"input"},
    {"field": "processing_fee_balance", "title": "Processing Fee Balance", "filterControl":"input"},
    {"field": "merchant_fee", "title": "Merchant Fee", "filterControl":"input"},
    {"field": "electricity_fee", "title": "Electricity Fee", "filterControl":"input"},
    {"field": "electricity_balance", "title": "Electricity Fee Balance", "filterControl":"input"},
    {"field": "electricity_request", "title": "Electricity Request", "filterControl":"input"},
    {"field": "food_merchant_agreement", "title": "Food Merchant Agreement", "filterControl":"select"},
    {"field": "estimated_date_of_arrival", "title": "Estimated Date of Arrival", "filterControl":"select"},
    {"field": "service_animal", "title": "Service Animal", "filterControl":"select"},
    {"field": "last_3_years", "title": "Last 3 Years", "filterControl":"select"},
    {"field": "vehicle_length", "title": "Vehicle Length", "filterControl":"input"},
    {"field": "vehicle_license_plate", "title": "Vehicle License Plate", "filterControl":"input"},
    {"field": "vehicle_state", "title": "Vehicle State", "filterControl":"input"},
    {"field": "trailer_length", "title": "Trailer Length", "filterControl":"input"},
    {"field": "trailer_license_plate", "title": "Trailer License Plate", "filterControl":"input"},
    {"field": "trailer_state", "title": "Trailer State", "filterControl":"input"},
    {"field": "notes", "title": "notes", "filterControl":"input"},
    {"field": "application_date", "title": "Application Date", "filterControl":"input"},
    {"field": "checkin_date", "title": "Checkin Date", "filterControl":"input"},
    {"field": "signature", "title": "Signature", "filterControl":"input"}
    ]
    rows = []
    full = Merchant.query.filter().all()
    for merch in full:
        reg_json = json.loads(merch.toJSON())
        rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

@bp.route("/merchant_invoices", methods=("GET", ""))
@login_required
@permission_required('merchant_reports')
def merchant_invoices():
    data = {}

    # {"field": "", "title": "", "filterControl":"input"}
    # invoice_number = db.Column(db.Integer(), db.ForeignKey("invoice.invoice_number"))
    # {"field": "", "title": "", "filterControl":"input"}
    # invoice = db.relationship("Invoice", back_populates="merchants")
    # {"field": "", "title": "", "filterControl":"input"}
    # payments = db.relationship("Payment", back_populates="merchant")
    # {"field": "", "title": "", "filterControl":"input"}

    columns = [{"field": "invoice_number", "title": "Invoice Number", "filterControl": 'input'},
    {"field": "invoice_type", "title": "Invoice Type", "filterControl": 'select'},
    {"field": "invoice_email", "title": "Invoice Email", "filterControl": 'input'},
    {"field": "invoice_date", "title": "Invoice Date", "filterControl":"select"},
    {"field": "invoice_status", "title": "Invoice Status", "filterControl":"select"},
    {"field": "space_fee", "title": "Space Fee", "filterControl":"input"},
    {"field": "processing_fee", "title": "Processing Fee", "filterControl":"select"},
    {"field": "invoice_total", "title": "Invoice Total", "filterControl":"input"},
    {"field": "balance", "title": "Balance", "filterControl":"input"},
    {"field": "notes", "title": "Notes", "filterControl":"input"},
    ]
    rows = []
    full = Invoice.query.filter(Invoice.invoice_type == 'MERCHANT').order_by(Invoice.invoice_number).all()
    for merch in full:
        reg_json = json.loads(merch.toJSON())
        rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

@bp.route("/registration_report", methods=("GET", ""))
@login_required
@permission_required('registration_reports')
def registration_report():
    data = {}
    columns = [{"field": "count", "title": "Count"},
        {"field": "date", "title": "Date", "filterControl":"input"},
        {"field": "time", "title": "Time CT", "filterControl":"input"},
        {"field": "name", "title": "Name", "filterControl":"input"},
        {"field": "business_name", "title": "Business Name", "filterControl":"input"},
        {"field": "email", "title": "Email", "filterControl":"input"},
        {"field": "invoice_number", "title": "Invoice Number", "filterControl":"input"},
        {"field": "invoice_status", "title": "Invoice Status", "filterControl":"input"},
        {"field": "reg_id", "title": "Registration Number", "filterControl":"input"},
        {"field": "reg_status", "title": "Registration Status", "filterControl":"input"},
        {"field": "reg_type", "title": "Registration Type", "filterControl":"input"},
        {"field": "invoice_total", "title": "Invoice Total", "filterControl":"input"},
        {"field": "mbr", "title": "Member", "filterControl":"input"},
        {"field": "adult_minor", "title": "Adult/Minor", "filterControl":"input"},
        {"field": "reg_base", "title": "Registration Base", "filterControl":"input"},
        {"field": "nmr", "title": "NMR", "filterControl":"input"},
        {"field": "donation", "title": "Donation", "filterControl":"input"},
        {"field": "space_fee", "title": "Space Fee", "filterControl":"input"},
        {"field": "processing_fee", "title": "Processing Fee", "filterControl":"input"},
        {"field": "rider_fee", "title": "Rider Fee", "filterControl":"input"},
        {"field": "total_price_paid", "title": "Total Price Paid", "filterControl":"input"},
    ]
    rows = []
    # invoices = Invoice.query.filter().all()
    regs = Registrations.query.filter().all()
    regs.extend(Merchant.query.filter().all())
    regs.extend(EarlyOnRequest.query.filter().all())
    obj = {}
    for field in columns:
        obj[field["field"]]=None
        count=1
    temp_list=[]
    for reg in regs:
        if reg.invoice != None:
            temp_obj = copy.deepcopy(obj)
            temp_obj = mapping_registration_report(reg,temp_obj,count)
            temp_list.append(temp_obj)
            reg_json = json.loads(toJSON(temp_obj))
            rows.append(reg_json)
            count+=1
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

def mapping_registration_report(obj,temp_obj,count):
    temp_obj['count']=count
    match obj.invoice.invoice_type:
        case 'REGISTRATION':
            temp_obj['date']=obj.reg_date_time.date()
            temp_obj['time']=obj.reg_date_time.time()
            temp_obj['name']=obj.fname + " " + obj.lname
            temp_obj['email']=obj.invoice_email
            temp_obj['invoice_number']=obj.invoice.invoice_number
            temp_obj['invoice_status']=obj.invoice.invoice_status
            temp_obj['reg_id']=obj.id
            temp_obj['reg_status']= '-' if obj.duplicate != True and obj.canceled != True else 'CANCELD/DUPLICATE'
            temp_obj['reg_type']=obj.invoice.invoice_type
            temp_obj['invoice_total']=obj.invoice.invoice_total
            temp_obj['mbr']=obj.mbr
            temp_obj['adult_minor']= obj.age if obj.age == '18+' or obj.age == "Royals" else 'Minor'
            temp_obj['reg_base']=obj.registration_price
            temp_obj['nmr']=obj.nmr_price
            temp_obj['donation']=obj.paypal_donation
            temp_obj['total_price_paid']=0
            if obj.invoice.payments != None:
                for reg_payment in obj.payments:
                    temp_obj['total_price_paid']+=reg_payment.amount
        case 'MERCHANT':
            temp_obj['date']=obj.application_date.date()
            temp_obj['time']=obj.application_date.time()
            temp_obj['name']=obj.fname + " " + obj.lname
            temp_obj['business_name']=obj.business_name
            temp_obj['email']=obj.email
            temp_obj['invoice_number']=obj.invoice.invoice_number
            temp_obj['invoice_status']=obj.invoice.invoice_status
            temp_obj['reg_id']=obj.id
            temp_obj['reg_status']= obj.status
            temp_obj['reg_type']=obj.invoice.invoice_type
            temp_obj['invoice_total']=obj.invoice.invoice_total
            temp_obj['space_fee']=obj.space_fee
            temp_obj['processing_fee']=obj.processing_fee
            temp_obj['total_price_paid']=0
            if obj.invoice.payments != None:
                for reg_payment in obj.payments:
                    temp_obj['total_price_paid']+=reg_payment.amount
        case 'EARLYON':
            temp_obj['date']=obj.request_date.date()
            temp_obj['time']=obj.request_date.time()
            temp_obj['name']=obj.registration.fname + " " + obj.registration.lname
            temp_obj['business_name']=obj.mercahnt.business_name if obj.mercahnt != None else None
            temp_obj['email']=obj.registration.invoice_email
            temp_obj['invoice_number']=obj.invoice.invoice_number
            temp_obj['invoice_status']=obj.invoice.invoice_status
            temp_obj['reg_id']=obj.id
            temp_obj['reg_status']= 'APPRVOED' if obj.dept_approval_status == 'APPROVED' and obj.autocrat_approval_status == 'APPROVED' else 'NOT APPROVED'
            temp_obj['reg_type']=obj.invoice.invoice_type
            temp_obj['invoice_total']=obj.invoice.invoice_total
            temp_obj['rider_fee']=obj.rider_cost
            temp_obj['total_price_paid']=0
            if obj.invoice.payments != None:
                for reg_payment in obj.payments:
                    temp_obj['total_price_paid']+=reg_payment.amount

    return temp_obj

def toJSON(obj):
    data_dict = {}
    for key in obj:
        if not key.startswith("_"):
            if isinstance(obj[key], datetime):
                data_dict[key] = datetime.strftime(obj[key], "%Y-%m-%d")
            else:
                data_dict[key] = obj[key]
    return json.dumps(data_dict, sort_keys=True, default=str)

@bp.route("/paypal_recon_export", methods=("GET", ""))
@login_required
@permission_required('registration_reports')
def paypal_recon_export():
    paypal_transactions = get_paypal_transactions()
    data = {}
    columns = [{"field": "invoice_status", "title": "Invoice Status", "filterControl":"input"},
        {"field": "date", "title": "Invoice Date", "filterControl":"input"},
        {"field": "email", "title": "Email", "filterControl":"input"},
        {"field": "invoice_id", "title": "PayPal ID", "filterControl":"input"},
        {"field": "invoice_number", "title": "Invoice Number", "filterControl":"input"},
        {"field": "invoice_type", "title": "Invoice Type", "filterControl":"input"},
        {"field": "paypal_gross", "title": "PayPal Gross", "filterControl":"input"},
        {"field": "paypal_fee", "title": "PayPal Fee", "filterControl":"input"},
        {"field": "paypal_net", "title": "PayPal Net", "filterControl":"input"},
        {"field": "other_payments", "title": "Non-PayPal Payments", "filterControl":"input"},
        {"field": "registration_total", "title": "Registration", "filterControl":"input"},
        {"field": "nmr_total", "title": "NMR", "filterControl":"input"},
        {"field": "donation_total", "title": "Donation", "filterControl":"input"},
        {"field": "space_fee", "title": "Space Fee", "filterControl":"input"},
        {"field": "processing_fee", "title": "Processing Fee", "filterControl":"input"},
        {"field": "rider_fee", "title": "Rider Fee", "filterControl":"input"},
        {"field": "invoice_total", "title": "Invoice Total", "filterControl":"input"},
        {"field": "total_price_paid", "title": "Total Price Paid", "filterControl":"input"},
        {"field": "balance", "title": "Invoice Balance", "filterControl":"input"},
    ]
    rows = []
    invoices = Invoice.query.filter().all()
    obj = {}
    for field in columns:
        obj[field["field"]]=None
    for inv in invoices:
        temp_obj = copy.deepcopy(obj)
        temp_obj = mapping_recon_report(inv,temp_obj,paypal_transactions)
        reg_json = json.loads(toJSON(temp_obj))
        rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

def mapping_recon_report(obj,temp_obj,paypal_transactions):
    temp_obj['invoice_status']=obj.invoice_status
    temp_obj['date']=obj.invoice_date.date()
    temp_obj['email']=obj.invoice_email
    temp_obj['invoice_id']=obj.invoice_id
    temp_obj['invoice_number']=obj.invoice_number
    temp_obj['invoice_type']=obj.invoice_type
    temp_obj['registration_total']=obj.registration_total
    temp_obj['nmr_total']=obj.nmr_total
    temp_obj['donation_total']=obj.donation_total
    temp_obj['space_fee']=obj.space_fee
    temp_obj['processing_fee']=obj.processing_fee
    temp_obj['rider_fee']=obj.rider_fee
    temp_obj['invoice_total']=obj.invoice_total
    temp_obj['balance']=obj.balance
    temp_obj['paypal_gross']=0
    temp_obj['paypal_fee']=0
    temp_obj['paypal_net']=0
    temp_obj['other_payments']=0
    temp_obj['total_price_paid']=0

    if obj.payments != None:
        for payment in obj.payments:
            temp_obj['total_price_paid']+=payment.amount
            if payment.type != 'PAYPAL':
                temp_obj['other_payments']+=payment.amount
            if payment.paypal_id != None:
                if payment.paypal_id in paypal_transactions:
                    pay = paypal_transactions[payment.paypal_id]
                    temp_obj['paypal_gross']=float(pay['gross'])
                    temp_obj['paypal_fee']=float(pay['fee'])
                    temp_obj['paypal_net']=float(pay['net'])

    return temp_obj

def toJSON(obj):
    data_dict = {}
    for key in obj:
        if not key.startswith("_"):
            if isinstance(obj[key], datetime):
                data_dict[key] = datetime.strftime(obj[key], "%Y-%m-%d")
            else:
                data_dict[key] = obj[key]
    return json.dumps(data_dict, sort_keys=True, default=str)

@bp.route("/land_pre-reg", methods=("GET", ""))
@login_required
@permission_required('registration_reports')
def land_pre_reg():
    data = {}
    columns = [{"field": "id", "title": "ID", "filterControl": 'input'},
        {"field": "fname", "title": "First Name", "filterControl":"input"},
        {"field": "lname", "title": "Last Name", "filterControl":"input"},
        {"field": "scaname", "title": "SCA Name", "filterControl":"input"},
        {"field": "age", "title": "Age", "filterControl":"select"},
        {"field": "reg_date_time", "title": "Registration Date/Time", "filterControl":"input"},
        {"field": "prereg", "title": "Pre-Registered", "filterControl":"select"},
        {"field": "expected_arrival_date", "title": "Expected Arrival Date", "filterControl":"select"},
        {"field": "early_on_approved", "title": "EarlyOn Approved", "filterControl":"select"},
        {"field": "invoice_number", "title": "Invoice Number", "filterControl":"input"},
        {"field": "invoice_status", "title": "Invoice Status", "filterControl":"input"},
        {"field": "kingdom", "title": "Kingdom", "filterControl":"input"},
        {"field": "lodging", "title": "Lodging", "filterControl":"input"},
    ]
    rows = []
    regs = Registrations.query.filter(Registrations.prereg==True,Registrations.canceled!=True,Registrations.duplicate!=True).order_by(Registrations.id).all()
    for reg in regs:
        if reg.invoice:
            if reg.invoice.invoice_status == 'PAID':
                kingdom = reg.kingdom.name
                lodging = reg.lodging.name
                reg_json = json.loads(reg.toJSON())
                reg_json['kingdom'] = kingdom
                reg_json['lodging'] = lodging
                reg_json['invoice_status'] = reg.invoice.invoice_status
                rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

@bp.route("/paypal_canceled_export", methods=("GET", ""))
@login_required
@permission_required('registration_reports')
def paypal_canceled_export():
    data = {}

    columns = [{"field": "invoice_number", "title": "Invoice Number", "filterControl": 'input'},
    {"field": "invoice_type", "title": "Invoice Type", "filterControl": 'select'},
    {"field": "invoice_email", "title": "Invoice Email", "filterControl": 'input'},
    {"field": "invoice_date", "title": "Invoice Date", "filterControl":"select"},
    {"field": "invoice_status", "title": "Invoice Status", "filterControl":"select"},
    {"field": "registration_total", "title": "Registration", "filterControl":"input"},
    {"field": "nmr_total", "title": "NMR", "filterControl":"input"},
    {"field": "donation_total", "title": "Donation", "filterControl":"input"},
    {"field": "space_fee", "title": "Space Fee", "filterControl":"input"},
    {"field": "processing_fee", "title": "Processing Fee", "filterControl":"input"},
    {"field": "rider_fee", "title": "Rider Fee", "filterControl":"input"},
    {"field": "invoice_total", "title": "Invoice Total", "filterControl":"input"},
    {"field": "balance", "title": "Balance", "filterControl":"input"},
    {"field": "notes", "title": "Notes", "filterControl":"input"},
    ]
    rows = []
    full = Invoice.query.filter(Invoice.invoice_status!='PAID',Invoice.invoice_status!='OPEN',).order_by(Invoice.invoice_number).all()
    for inv in full:
        reg_json = json.loads(inv.toJSON())
        rows.append(reg_json)
    data['columns'] = columns
    data['rows'] = rows
    return jsonify(data)

@bp.route("/paypal_transactions", methods=("GET", ""))
@login_required
@permission_required('admin')
def paypal_transaction_search():
    return str(get_paypal_transactions())