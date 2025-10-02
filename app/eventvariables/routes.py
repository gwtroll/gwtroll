from flask import render_template
from app.eventvariables import bp

from flask_login import login_required
from flask import render_template, request, redirect, url_for, flash
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from app.utils.security_utils import *
from flask_security import roles_accepted

@bp.route('/', methods=('GET', 'POST'))
@login_required
@permission_required('admin')
def eventvariables():

    eventvariables = EventVariables.query.first()
    if not eventvariables:
        form = EventVariablesForm()
    else:
        form = EventVariablesForm(
            name=eventvariables.name,
            year=eventvariables.year,
            event_title=eventvariables.event_title,
            start_date=eventvariables.start_date,
            end_date=eventvariables.end_date,
            location=eventvariables.location,
            description=eventvariables.description,
            preregistration_open_date=eventvariables.preregistration_open_date,
            preregistration_close_date=eventvariables.preregistration_close_date,
            autocrat1=eventvariables.autocrat1,
            autocrat2=eventvariables.autocrat2,
            autocrat3=eventvariables.autocrat3,
            reservationist=eventvariables.reservationist,
            merchant_application_deadline=eventvariables.merchant_application_deadline,
            merchantcrat_email=eventvariables.merchantcrat_email,
            marchantcrat_phone=eventvariables.marchantcrat_phone,
            merchant_preregistration_open_date=eventvariables.merchant_preregistration_open_date,
            merchant_preregistration_close_date=eventvariables.merchant_preregistration_close_date,
            merchant_processing_fee=eventvariables.merchant_processing_fee,
            merchant_late_processing_fee=eventvariables.merchant_late_processing_fee,
            merchant_squarefoot_fee=eventvariables.merchant_squarefoot_fee,
            merchant_bounced_check_fee=eventvariables.merchant_bounced_check_fee
        )

    if request.method == 'POST' and form.validate_on_submit():
        if not eventvariables:
            eventvariables = EventVariables(
                name=form.name.data,
                year=form.year.data,
                event_title=form.event_title.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                location=form.location.data,
                description=form.description.data,
                preregistration_open_date=form.preregistration_open_date.data,
                preregistration_close_date=form.preregistration_close_date.data,
                autocrat1=form.autocrat1.data,
                autocrat2=form.autocrat2.data,
                autocrat3=form.autocrat3.data,
                reservationist=form.reservationist.data,
                merchant_application_deadline=form.merchant_application_deadline.data,
                merchantcrat_email=form.merchantcrat_email.data,
                marchantcrat_phone=form.marchantcrat_phone.data,
                merchant_preregistration_open_date=form.merchant_preregistration_open_date.data,
                merchant_preregistration_close_date=form.merchant_preregistration_close_date.data,
                merchant_processing_fee=form.merchant_processing_fee.data,
                merchant_late_processing_fee=form.merchant_late_processing_fee.data,
                merchant_squarefoot_fee=form.merchant_squarefoot_fee.data,
                merchant_bounced_check_fee=form.merchant_bounced_check_fee.data
            )
            db.session.add(eventvariables)
        else:
            eventvariables.name = form.name.data
            eventvariables.year = form.year.data
            eventvariables.event_title = form.event_title.data
            eventvariables.start_date = form.start_date.data
            eventvariables.end_date = form.end_date.data
            eventvariables.location = form.location.data
            eventvariables.description = form.description.data
            eventvariables.preregistration_open_date = form.preregistration_open_date.data
            eventvariables.preregistration_close_date = form.preregistration_close_date.data
            eventvariables.autocrat1 = form.autocrat1.data
            eventvariables.autocrat2 = form.autocrat2.data
            eventvariables.autocrat3 = form.autocrat3.data
            eventvariables.reservationist = form.reservationist.data
            eventvariables.merchant_application_deadline = form.merchant_application_deadline.data
            eventvariables.merchantcrat_email = form.merchantcrat_email.data
            eventvariables.marchantcrat_phone = form.marchantcrat_phone.data
            eventvariables.merchant_preregistration_open_date = form.merchant_preregistration_open_date.data
            eventvariables.merchant_preregistration_close_date = form.merchant_preregistration_close_date.data
            eventvariables.merchant_processing_fee = form.merchant_processing_fee.data
            eventvariables.merchant_late_processing_fee = form.merchant_late_processing_fee.data
            eventvariables.merchant_squarefoot_fee = form.merchant_squarefoot_fee.data
            eventvariables.merchant_bounced_check_fee = form.merchant_bounced_check_fee.data
        
        db.session.commit()
        flash('Event Variables saved successfully!', 'success')
        return redirect(url_for('eventvariables.eventvariables', form=form))

    return render_template('edit_eventvariables.html', form=form)

@bp.route('/pricesheet', methods=('GET', 'POST'))
@login_required
@permission_required('admin')
def pricesheet():
    pricesheet = PriceSheet.query.order_by(PriceSheet.arrival_date).all()
    return render_template('viewpricesheet.html', pricesheet=pricesheet)


@bp.route('/pricesheet/<date>', methods=('GET', 'POST'))
@login_required
@permission_required('admin')
def editpricesheet(date):
    pricesheet = PriceSheet.query.filter(PriceSheet.arrival_date == date).first()
    form = PriceSheetForm(
        arrival_date = pricesheet.arrival_date.strftime('%Y/%m/%d'),
        prereg_price = pricesheet.prereg_price,
        atd_price = pricesheet.atd_price
    )
    form.arrival_date.choices = get_reg_arrival_dates()
    if request.method == 'POST' and form.validate_on_submit():
        pricesheet.prereg_price = form.prereg_price.data
        pricesheet.atd_price = form.atd_price.data
        db.session.commit()
        return redirect(url_for('eventvariables.pricesheet'))
    print(form.errors)
    return render_template('editpricesheet.html', form=form, pricesheet=pricesheet)

@bp.route('/paypal_info', methods=('GET', 'POST'))
@login_required
@permission_required('admin')
def paypal_info():
    form=PayPalForm()
    if request.method=='POST':
        env_vars=EventVariables.query.filter(EventVariables.id==1).first()
        env_vars.bas=form.base_url.data
        env_vars.cli=form.client_id.data
        env_vars.sec=form.client_secret.data
        env_vars.web=form.webhook_id.data
        db.session.commit()
        return redirect(url_for('eventvariables.eventvariables'))
    return render_template('paypal_info.html', form=form)