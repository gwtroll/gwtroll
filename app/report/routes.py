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
    form.report_type.choices = [('royal_registrations', 'royal_registrations'), ('land_pre-reg', 'land_pre-reg'), ('full_export', 'full_export'), ('full_signatue_export', 'full_signature_export'), ('full_checkin_report', 'full_checkin_report'), ('at_door_count', 'at_door_count'), ('kingdom_count', 'kingdom_count'), ('ghost_report', 'ghost_report'), ('early_on_report','early_on_report'), ('paypal_paid_export','paypal_paid_export'),('paypal_canceled_export','paypal_canceled_export'),('paypal_recon_export','paypal_recon_export'),('atd_export','atd_export'),('log_export','log_export'),('minor_waivers','minor_waivers')]
    return render_template("viewreport.html", form=form)


@bp.route("/merchant", methods=("GET", "POST"))
@login_required
@permission_required('merchant_reports')
def merchant_reports():
    form = ReportForm()
    form.report_type.choices = [('merchant_full_export','Full Export'),('merchant_invoices','Merchant Invoices')]
    return render_template("viewreport.html", form=form)