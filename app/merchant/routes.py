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

@bp.route('/search', methods=('GET','POST'))
@login_required
@roles_accepted('Admin','Merchant Head','Department Head')
def merchant_search():
    merchant_count = 0
    if request.method == "POST":
        if request.form.get('search_name'):
            search_value = request.form.get('search_name')
            print(search_value)
            if search_value is not None and search_value != '':
                    merchants = query_db(
                    "SELECT * FROM merchant WHERE (fname ILIKE %s OR lname ILIKE %s OR sca_name ILIKE %s) Order by checkin_date DESC, business_name, lname, fname",
                    #(search_value, search_value, search_value))
                    ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))

        elif request.form.get('business_name'):
            search_value = request.form.get('business_name')
            merchants = query_db(
                "SELECT * FROM merchant WHERE (business_name ILIKE %s) Order by checkin_date DESC, business_name, lname, fname",
                ('%' + search_value + '%',))

        else:
            return render_template('merchant_search.html', merchant_count=merchant_count)

            # if (arrival_date == datetime.strptime('03/08/2025','%m/%d/%Y') or arrival_date <= datetime.now()):
            #     r['expected_arrival_date'] = arrival_date
            #     r['ready_for_checkin'] = True
            # else:
            #     r['expected_arrival_date'] = arrival_date
            #     r['ready_for_checkin'] = False
        return render_template('merchant_search.html', merchants=merchants, merchant_count=merchant_count)
    else:
        return render_template('merchant_search.html', merchant_count=merchant_count)

@bp.route('/checkin/<int:merchantid>', methods=('GET','POST'))
@login_required
@roles_accepted('Admin','Merchant Head','Department Head')
def merchant_checkin(merchantid):
    merchant = Merchant.query.filter_by(id=merchantid).first()
    payments = Payment.query.filter_by(merchant_id=merchantid).all()
    electricity_fee_form = MerchantElectricityForm(
        electricity_request=merchant.electricity_request,
        electricity_fee=merchant.electricity_fee,
        electricity_balance=merchant.electricity_balance,
    )
    payment_form = PayRegistrationForm()
    payment_form.total_due.data = merchant.electricity_balance + merchant.processing_fee_balance + merchant.space_fee_balance
    form = MerchantCheckinForm(
        notes=merchant.notes,
    )
    if request.method == 'POST':
        if form.validate_on_submit():
            merchant.notes = form.notes.data
            merchant.checkin_date = datetime.today().replace(microsecond=0)
            db.session.commit()
            flash('Merchant {} checked in successfully.'.format(merchant.business_name), 'success')
            return redirect(url_for('merchant.merchant_search'))

    return render_template('merchant_checkin.html', merchant=merchant, payments=payments, form=form, electricity_fee_form=electricity_fee_form, payment_form=payment_form)

@bp.route('/<int:merchantid>/electricityfee', methods=('GET','POST'))
@login_required
@roles_accepted('Admin','Merchant Head','Department Head')
def merchant_electricityfee(merchantid):
    merchant = Merchant.query.filter_by(id=merchantid).first()
    
    if request.method == 'POST':
        if request.form.get('electricity_fee'):
            payments = Payment.query.filter_by(merchant_id=merchantid).all()
            electricity_fee_paid = 0
            for payment in payments:
                electricity_fee_paid += payment.electricity_fee_amount
            merchant.electricity_request= request.form.get('electricity_request')
            merchant.electricity_fee = request.form.get('electricity_fee')
            merchant.electricity_balance = float(merchant.electricity_fee) - float(electricity_fee_paid)
            db.session.commit()

    return redirect(url_for("merchant.merchant_checkin",merchantid=merchant.id))

@bp.route('/<int:merchantid>/payment', methods=('GET','POST'))
@login_required
@roles_accepted('Admin','Merchant Head','Department Head')
def merchant_payment(merchantid):
    merchant = Merchant.query.filter_by(id=merchantid).first()

    if request.method == 'POST':

        pay = Payment(
            type = request.form.get('payment_type'),
            payment_date = datetime.now().date(),
            amount = request.form.get('total_due'),
            processing_fee_amount = merchant.processing_fee_balance,
            space_fee_amount = merchant.space_fee_balance,
            electricity_fee_amount = merchant.electricity_balance,
            merchant_id = merchant.id,
            # event_id = reg.event_id
        )

        db.session.add(pay)

        merchant.electricity_balance = 0
        merchant.processing_fee_balance = 0
        merchant.space_fee_balance = 0

        db.session.commit()

        return redirect(url_for("merchant.merchant_checkin",merchantid=merchant.id))


@bp.route('/fastpass')
def merchant_fastpass():
        return render_template('merchant_fastpass.html')

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
        application_date = datetime.strptime(str(merchant.application_date), '%Y-%m-%d %H:%M:%S') if merchant.application_date else None,
        signature = merchant.signature if merchant.signature else ''
    )

    if request.method == 'POST':
        old_status = merchant.status
        if form.validate_on_submit():
            merchant.status = form.status.data
            merchant.application_date = form.application_date.data.replace(microsecond=0)
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
            application_date = datetime.today().replace(microsecond=0),
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