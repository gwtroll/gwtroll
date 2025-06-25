from app.marshal import bp
import os
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from flask_security import roles_accepted
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import current_user, login_required
import requests

@bp.route('/', methods=['GET', 'POST'])
@roles_accepted('Admin','Marshal Admin','Marshal User')
def index():
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
            return render_template('marshal_home.html', searchreg=reg, inspection_stats=inspection_stats)
        elif request.form.get('mbrnum_id'):
            search_value = request.form.get('mbrnum_id')
            reg = query_db(
                "SELECT * FROM registrations WHERE mbr_num = %s AND checkin IS NOT NULL order by lname, fname",
                (int(search_value),))
            return render_template('marshal_home.html', searchreg=reg, inspection_stats=inspection_stats)
        elif request.form.get('medallion'):
            search_value = request.form.get('medallion')
            reg = query_db(
                "SELECT * FROM registrations WHERE medallion = %s order by lname, fname",
                (search_value,))
            return render_template('marshal_home.html', searchreg=reg, inspection_stats=inspection_stats)
        else:
            return render_template('marshal_home.html', inspection_stats=inspection_stats)
    else:
        return render_template('marshal_home.html', inspection_stats=inspection_stats)
    
@bp.route('/<int:regid>/addbow', methods=('GET', 'POST'))
@roles_accepted('Admin','Marshal Admin','Marshal User')
def add_bow(regid):
    reg = get_reg(regid)
    form = BowForm()
    if request.method == 'POST':
        if request.form.get("poundage"):
            update_reg = Registrations.query.filter_by(id=reg.id).first()
            bow = Bows()
            bow.poundage = request.form.get("poundage")
            bow.bow_inspection_marshal_id = current_user.id
            bow.bow_inspection_date = datetime.now()
            if update_reg.bows:
                update_reg.bows.append(bow)
            else:
                bows = []
                bows.append(bow)
                update_reg.bows = bows
            db.session.commit()
        return redirect(url_for('marshal.reg', regid=regid))
    return render_template('add_bow.html', reg=reg, form=form)

@bp.route('/<int:regid>/addcrossbow', methods=('GET', 'POST'))
@roles_accepted('Admin','Marshal Admin','Marshal User')
def add_crossbow(regid):
    reg = get_reg(regid)
    form = BowForm()
    if request.method == 'POST':
        print('POSTED')
        if request.form.get("poundage"):
            print('Poundage')
            print(request.form.get("poundage"))
            update_reg = Registrations.query.filter_by(id=reg.id).first()
            print(request.form.get("poundage"))
            crossbow = Crossbows()
            crossbow.inchpounds = request.form.get("poundage")
            crossbow.crossbow_inspection_marshal_id = current_user.id
            crossbow.crossbow_inspection_date = datetime.now()
            if update_reg.crossbows:
                update_reg.crossbows.append(crossbow)
            else:
                crossbows = []
                crossbows.append(crossbow)
                update_reg.crossbows = crossbows
            print('YEP')
            db.session.commit()
        return redirect(url_for('marshal.reg', regid=regid))
    return render_template('add_crossbow.html', reg=reg, form=form)

@bp.route('/<int:regid>/addincident', methods=('GET', 'POST'))
@roles_accepted('Admin','Marshal Admin','Marshal User')
def incident(regid):
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

        return redirect(url_for('marshal.reg', regid=regid))
    return render_template('add_crossbow.html', reg=reg, form=form)

@bp.route('/<int:regid>', methods=('GET', 'POST'))
@roles_accepted('Admin','Marshal Admin','Marshal User')
def reg(regid):
    reg = get_reg(regid)
    form = MarshalForm()
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
    inspections = MarshalInspection.query.filter(MarshalInspection.regid == regid).all()
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

        print(chivalric_inspection, chivalric_spear_inspection, rapier_inspection, rapier_spear_inspection, combat_archery_inspection)

        if 'Heavy' not in inspection_dict and chivalric_inspection:
            new_inspection = MarshalInspection(
                regid = regid,
                inspection_type = 'Heavy',
                inspection_date = datetime.now(),
                inspecting_marshal_id = current_user.id,
                inspected = True
            )
            print('Adding Heavy Inspection')
            db.session.add(new_inspection)
        if 'Heavy Spear' not in inspection_dict and chivalric_spear_inspection:
            new_inspection = MarshalInspection(
                regid = regid,
                inspection_type = 'Heavy Spear',
                inspection_date = datetime.now(),
                inspecting_marshal_id = current_user.id,
                inspected = True
            )
            db.session.add(new_inspection)
        if 'Rapier' not in inspection_dict and rapier_inspection:
            new_inspection = MarshalInspection(
                regid = regid,
                inspection_type = 'Rapier',
                inspection_date = datetime.now(),
                inspecting_marshal_id = current_user.id,
                inspected = True
            )
            db.session.add(new_inspection)
        if 'Rapier Spear' not in inspection_dict and rapier_spear_inspection:
            new_inspection = MarshalInspection(
                regid = regid,
                inspection_type = 'Rapier Spear',
                inspection_date = datetime.now(),
                inspecting_marshal_id = current_user.id,
                inspected = True
            )
            db.session.add(new_inspection)
        if 'Combat Archery' not in inspection_dict and combat_archery_inspection:
            new_inspection = MarshalInspection(
                regid = regid,
                inspection_type = 'Combat Archery',
                inspection_date = datetime.now(),
                inspecting_marshal_id = current_user.id,
                inspected = True
            )
            db.session.add(new_inspection)

        db.session.commit()
        return redirect(url_for('marshal.reg',regid=regid))
    return render_template('marshal_reg.html', reg=reg, form=form, bow_form=bow_form, inspection_dict=inspection_dict, incident_form=incident_form, fighter_auth=fighter_auth)

@bp.route('/reports', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Marshal Admin')
def reports():
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

        rptquery = "SELECT id, (SELECT fname FROM registrations WHERE registrations.id = marshal_inspection.id) AS \"Reg_FName\", (SELECT lname FROM registrations WHERE registrations.id = marshal_inspection.id) AS \"Reg_LName\", inspection_type, inspection_date, (SELECT fname FROM users WHERE users.id = marshal_inspection.inspecting_marshal_id) AS \"Marshal_FName\", (SELECT lname FROM users WHERE users.id = marshal_inspection.inspecting_marshal_id) AS \"Marshal_LName\", (SELECT medallion FROM users WHERE users.id = marshal_inspection.inspecting_marshal_id) AS \"Marshal_Medallion\" FROM marshal_inspection"
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

        rptquery = "SELECT id, (SELECT fname FROM registrations WHERE registrations.id = incidentreport.id) AS \"Reg_FName\", (SELECT lname FROM registrations WHERE registrations.id = incidentreport.id) AS \"Reg_LName\", report_date, incident_date, (SELECT fname FROM users WHERE users.id = incidentreport.reporting_user_id) AS \"Marshal_FName\", (SELECT lname FROM users WHERE users.id = incidentreport.reporting_user_id) AS \"Marshal_LName\", notes FROM incidentreport"
        df = pd.read_sql_query(rptquery, engine)
        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        writer = pd.ExcelWriter(path1, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Report' ,index = False)
        worksheet = writer.sheets['Report']
        writer.close()
        return send_file(path2)
    return render_template('reports.html', form=form)