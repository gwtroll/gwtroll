from flask import render_template
from app.merchant import bp

from flask_login import current_user, login_required
from flask import render_template, request, url_for, flash, redirect
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from app.utils.email_utils import *

from flask_security import roles_accepted
from markupsafe import Markup

@bp.route('/', methods=('GET',))
@login_required
@roles_accepted('Admin','Merchant Head','Department Head')
def merchants():
    merchants = Merchant.query.all()
    return render_template('merchant_list.html', merchants=merchants)

@bp.route('/<int:merch_id>', methods=('GET','POST'))
@login_required
@roles_accepted('Admin','Merchant Head','Department Head')
def update(merch_id):
    merchant = Merchant.query.get_or_404(merch_id)
    form = EditMerchantForm(
        business_name = merchant.business_name,
        sca_name = merchant.sca_name,
        fname = merchant.fname,
        lname = merchant.lname,
        email = merchant.email,
        phone = merchant.phone,
        text_permission = merchant.text_permission,
        address = merchant.address,
        city = merchant.city,
        state_province = merchant.state_province,
        zip = merchant.zip,
        frontage_width = merchant.frontage_width,
        frontage_depth = merchant.frontage_depth,
        space_fee = merchant.space_fee,
        additional_space_information = merchant.additional_space_information,
        processing_fee = merchant.processing_fee,
        merchant_fee = merchant.merchant_fee,
        electricity_request = merchant.electricity_request,
        food_merchant_agreement = merchant.food_merchant_agreement,
        estimated_date_of_arrival = merchant.estimated_date_of_arrival,
        service_animal = merchant.service_animal,
        last_3_years = merchant.last_3_years,
        vehicle_length = merchant.vehicle_length,
        vehicle_license_plate = merchant.vehicle_license_plate,
        vehicle_state = merchant.vehicle_state,
        trailer_length = merchant.trailer_length, 
        trailer_license_plate = merchant.trailer_license_plate,
        trailer_state = merchant.trailer_state,
        notes = merchant.notes,
        status = merchant.status,
    )

    if request.method == 'POST':
        old_status = merchant.status
        if form.validate_on_submit():
            merchant.status = form.status.data
            merchant.business_name = form.business_name.data
            merchant.sca_name = form.sca_name.data
            merchant.fname = form.fname.data
            merchant.lname = form.lname.data
            merchant.email = form.email.data
            merchant.phone = form.phone.data
            merchant.text_permission = bool(form.text_permission.data)
            merchant.address = form.address.data
            merchant.city = form.city.data
            merchant.state_province = form.state_province.data
            merchant.zip = form.zip.data
            merchant.frontage_width = int(form.frontage_width.data) if form.frontage_width.data else 0
            merchant.frontage_depth = int(form.frontage_depth.data) if form.frontage_depth.data else 0
            merchant.additional_space_information = form.additional_space_information.data
            merchant.electricity_request = form.electricity_request.data
            merchant.food_merchant_agreement = form.food_merchant_agreement.data
            merchant.estimated_date_of_arrival = form.estimated_date_of_arrival.data
            merchant.service_animal = form.service_animal.data
            merchant.last_3_years = form.last_3_years.data
            merchant.vehicle_length = int(form.vehicle_length.data) if form.vehicle_length.data else 0
            merchant.vehicle_license_plate = form.vehicle_license_plate.data
            merchant.vehicle_state = form.vehicle_state.data
            merchant.trailer_length = int(form.trailer_length.data) if form.trailer_length.data else 0
            merchant.trailer_license_plate = form.trailer_license_plate.data
            merchant.trailer_state = form.trailer_state.data
            merchant.notes = form.notes.data
            merchant.space_fee = int(form.frontage_width.data) * int(form.frontage_depth.data) * .10 if form.frontage_width.data and form.frontage_depth.data else 0
            merchant.processing_fee = int(form.processing_fee.data)
            merchant.merchant_fee = merchant.processing_fee + merchant.space_fee
            db.session.commit()
            if old_status != merchant.status:
                if merchant.status == 'APPROVED':
                    send_merchant_approval_email(merchant.email, merchant)
                elif merchant.status == 'DENIED':
                    send_merchant_denial_email(merchant.email, merchant)
            return render_template('merchant_list.html', merchants=Merchant.query.all())
        print(form.errors)
        flash('There was an error with your submission. Please check the form and try again.', 'error')
    return render_template('edit_merchant.html', form=form, merchant=merchant)


@bp.route('/registration', methods=('GET', 'POST'))
def createprereg():
    # Close Merchants at Midnight MM/DD/YYYY
    # if datetime.now().date() >= datetime.strptime('02/22/2025','%m/%d/%Y').date():
    #     return render_template("prereg_closed.html")

    form = MerchantForm()
    print("Form Created")
    
    if form.validate_on_submit() and request.method == 'POST':
        print("Form Validated")

        merchant = Merchant(
            business_name = form.business_name.data,
            sca_name = form.sca_name.data,
            fname = form.fname.data,
            lname = form.lname.data,
            email =  form.email.data,
            phone = form.phone.data,
            text_permission = form.text_permission.data,
            address = form.address.data,
            city = form.city.data,
            state_province = form.state_province.data,
            zip = form.zip.data,
            frontage_width = form.frontage_width.data,
            frontage_depth = form.frontage_depth.data,
            space_fee = int(form.frontage_width.data)* int(form.frontage_depth.data) * .10,  # 10 cent per square foot
            additional_space_information = form.additional_space_information.data,
            processing_fee = 20 if datetime.today() < datetime(2025, 11, 19) else 45,
            electricity_request = form.electricity_request.data,
            food_merchant_agreement = form.food_merchant_agreement.data,
            estimated_date_of_arrival = form.estimated_date_of_arrival.data,
            service_animal = form.service_animal.data,
            last_3_years = form.last_3_years.data,
            vehicle_length = form.vehicle_length.data,
            vehicle_license_plate = form.vehicle_license_plate.data,
            vehicle_state = form.vehicle_state.data,
            trailer_length = form.trailer_length.data,
            trailer_license_plate = form.trailer_license_plate.data,
            trailer_state = form.trailer_state.data,
            signature = form.signature.data,
        )
        merchant.merchant_fee = merchant.processing_fee + merchant.space_fee,
        merchant.space_fee_balance = merchant.space_fee
        merchant.processing_fee_balance = merchant.processing_fee

        db.session.add(merchant)
        db.session.commit()

        send_merchant_confirmation_email(merchant.email,merchant)
        flash('Merchant Application {} created for {}.'.format(
        merchant.id, merchant.business_name))

        return redirect(url_for('merchant.success', merchantid=merchant.id))
    elif request.method == 'POST' and not form.validate_on_submit():
        print(form.errors)
    return render_template('create_merchant.html', form=form)

@bp.route('/success')
def success():
    merchantid = request.args.get('merchantid')
    return render_template('merchant_success.html', merchantid=merchantid)