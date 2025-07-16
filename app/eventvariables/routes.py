from flask import render_template
from app.eventvariables import bp

from flask_login import login_required
from flask import render_template, request, redirect, url_for, flash
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted

@bp.route('/', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
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
            merchant_application_deadline=eventvariables.merchant_application_deadline,
            merchantcrat_email=eventvariables.merchantcrat_email,
            marchantcrat_phone=eventvariables.marchantcrat_phone,
            preregistration_open_date=eventvariables.preregistration_open_date,
            preregistration_close_date=eventvariables.preregistration_close_date,
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
                merchant_application_deadline=form.merchant_application_deadline.data,
                merchantcrat_email=form.merchantcrat_email.data,
                marchantcrat_phone=form.marchantcrat_phone.data,
                preregistration_open_date=form.preregistration_open_date.data,
                preregistration_close_date=form.preregistration_close_date.data,
                merchant_preregistration_open_date=form.merchant_preregistration_open_date.data,
                merchant_preregistration_close_date=form.merchant_preregistration_close_date.data,
                merchant_processing_fee=form.merchant_processing_fee.data,
                merchant_late_processing_fee=form.merchant_late_processing_fee.data,
                merchant_squarefoot_fee=form.merchant_squarefoot_fee.data,
                merchant_bounced_check_fee=form.merchant_bounced_check_fee.data
            )
            print("Event Variables Updated")
            db.session.add(eventvariables)
        else:
            eventvariables.name = form.name.data
            eventvariables.year = form.year.data
            eventvariables.event_title = form.event_title.data
            eventvariables.start_date = form.start_date.data
            eventvariables.end_date = form.end_date.data
            eventvariables.location = form.location.data
            eventvariables.description = form.description.data
            eventvariables.merchant_application_deadline = form.merchant_application_deadline.data
            eventvariables.merchantcrat_email = form.merchantcrat_email.data
            eventvariables.marchantcrat_phone = form.marchantcrat_phone.data
            eventvariables.preregistration_open_date = form.preregistration_open_date.data
            eventvariables.preregistration_close_date = form.preregistration_close_date.data
            eventvariables.merchant_preregistration_open_date = form.merchant_preregistration_open_date.data
            eventvariables.merchant_preregistration_close_date = form.merchant_preregistration_close_date.data
            eventvariables.merchant_processing_fee = form.merchant_processing_fee.data
            eventvariables.merchant_late_processing_fee = form.merchant_late_processing_fee.data
            eventvariables.merchant_squarefoot_fee = form.merchant_squarefoot_fee.data
            eventvariables.merchant_bounced_check_fee = form.merchant_bounced_check_fee.data
        
        db.session.commit()
        print("Event Variables Saved")
        flash('Event Variables saved successfully!', 'success')
        return redirect(url_for('eventvariables.eventvariables', form=form))

    print(form.errors)

    return render_template('edit_eventvariables.html', form=form)