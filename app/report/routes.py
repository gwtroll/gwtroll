from flask import render_template
from app.report import bp
from app.utils.security_utils import *
from flask_login import login_required
from flask import render_template, request, redirect, url_for
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted


@bp.route("/", methods=("GET", "POST"))
@login_required
@permission_required("registration_reports")
def reports():
    form = ReportForm()
    if current_user.has_role('Land'):
        form.report_type.choices = [('registration_report','Registration Report'), ('royal_registrations', 'Royal Registrations'), ('land_pre-reg', 'Land Pre-Reg'), ('kingdom_count', 'Kingdom Count'), ('early_on_report','Early On Report')]
    else:
        form.report_type.choices = [('registration_report','Registration Report'),('royal_registrations', 'Royal Registrations'), ('land_pre-reg', 'Land Pre-Reg'), ('full_export', 'Full Export'), ('full_signatue_export', 'Full Signature Export'), ('full_checkin_report', 'Full Checkin Report'), ('at_door_count', 'At Door Count'), ('kingdom_count', 'Kingdom Count'), ('ghost_report', 'Ghost Report'), ('early_on_report','Early On Report'), ('paypal_paid_export','PayPal Paid Export'),('paypal_canceled_export','PayPal Canceled Export'),('paypal_recon_export','PayPal Recon Export'),('atd_export','ATD Export'),('log_export','Log Export'),('minor_waivers','Minor Waivers'),('paypal_transactions','PayPal Transactions')]
    return render_template("viewreport.html", form=form)


@bp.route("/merchant", methods=("GET", "POST"))
@login_required
@permission_required('merchant_reports')
def merchant_reports():
    form = ReportForm()
    form.report_type.choices = [('merchant_full_export','Full Export'),('merchant_invoices','Merchant Invoices'), ('merchant_early_on_report','Merchant Early On Report')]
    return render_template("viewreport.html", form=form)

@bp.route("/marshal", methods=("GET", "POST"))
@login_required
@permission_required('marshal_reports')
def marshal_reports():
    form = ReportForm()
    form.report_type.choices = [('full_inspection_report','Inspections'),('full_bows_crossbows','Bows/Crossbows'),('full_incident_report','Incidents')]
    return render_template("viewreport.html", form=form)