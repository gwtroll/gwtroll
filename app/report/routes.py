from io import BytesIO

from flask import render_template, send_file
from app import report
from app.report import bp
from app.utils.security_utils import *
from flask_login import login_required
from flask import render_template, request, redirect, url_for
from app.forms import *
from app.models import *
from app.utils.db_utils import *
import app.api.routes as api
import pandas as pd

from flask_security import roles_accepted


@bp.route("/", methods=("GET", "POST"))
@login_required
@permission_required("registration_reports")
def reports():
    form = ReportForm()
    if current_user.has_role('Land'):
        form.report_type.choices = [('registration_report','Registration Report'), ('royal_registrations', 'Royal Registrations'), ('land_pre_reg', 'Land Pre-Reg'), ('kingdom_count', 'Kingdom Count'), ('early_on_report','Early On Report')]
    else:
        form.report_type.choices = [('new_report','New Report'),('registration_report','Registration Report'),('royal_registrations', 'Royal Registrations'), ('land_pre_reg', 'Land Pre-Reg'), ('full_export', 'Full Export'), ('full_signatue_export', 'Full Signature Export'), ('full_checkin_report', 'Full Checkin Report'), ('at_door_count', 'At Door Count'), ('kingdom_count', 'Kingdom Count'), ('ghost_report', 'Ghost Report'), ('early_on_report','Early On Report'), ('paypal_paid_export','PayPal Paid Export'),('paypal_canceled_export','PayPal Canceled Export'),('paypal_recon_export','PayPal Recon Export'),('atd_export','ATD Export'),('troll_checkin_count','Troll Checkin Audit'),('log_export','Log Export'),('minor_waivers','Minor Waivers'),('paypal_transactions','PayPal Transactions'),('atd_payments','ATD Payments')]
    if current_user.has_role('Admin'):
        form.report_type.choices.append(('early_on_audit','Early On Report Audit'))
    return render_template("viewreport.html", form=form)


@bp.route("/merchant", methods=("GET", "POST"))
@login_required
@permission_required('merchant_reports')
def merchant_reports():
    form = ReportForm()
    form.report_type.choices = [('merchant_full_export','Full Export'),('merchant_invoices','Merchant Invoices'), ('merchant_early_on_report','Merchant Early On Report'), ('merchant_atd_payments','Merchant At-Door Payments')]
    return render_template("viewreport.html", form=form)

@bp.route("/marshal", methods=("GET", "POST"))
@login_required
@permission_required('marshal_reports')
def marshal_reports():
    form = ReportForm()
    form.report_type.choices = [('full_inspection_report','Inspections'),('full_bows_crossbows','Bows/Crossbows'),('full_incident_report','Incidents')]
    return render_template("viewreport.html", form=form)

@bp.route("/<report_name>/download", methods=("GET", "POST"))
@login_required
@permission_required("registration_reports")
def download_report(report_name):
    report = getattr(api, report_name)().json
    new_dict = {}
    for col in report['columns']:
        new_dict[col['field']] = []
    for row in report['rows']:
        for key in row:
            if key in new_dict:
                new_dict[key].append(row[key])
    df = pd.DataFrame(new_dict)

        # 2. Set up the in-memory buffer
    output = BytesIO()
    
    # 3. Write to the buffer using ExcelWriter
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    # 4. Seek to the beginning of the stream
    output.seek(0)

    report_name = report_name+"_"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".xlsx"

    # Export to an Excel file
    return send_file(output, download_name=report_name, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')