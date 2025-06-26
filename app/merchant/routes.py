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
def merchants():
    merchants = Merchant.query.all()
    return render_template('merchant_list.html', merchants=merchants)

@bp.route('/<int:merch_id>', methods=('GET','POST'))
def update(merch_id):
    merchant = Merchant.query.get_or_404(merch_id)
    form = MerchantForm(
        business_name = merchant.business_name,
        sca_name = merchant.sca_name,
        fname = merchant.fname,
        lname = merchant.lname,
        email = merchant.email,
        phone = merchant.phone,
        text_permission = merchant.text_permission,
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
        # food_merchant_agreement = merchant.food_merchant_agreement,
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
            merchant.city = form.city.data
            merchant.state_province = form.state_province.data
            merchant.zip = form.zip.data
            merchant.frontage_width = int(form.frontage_width.data)
            merchant.frontage_depth = int(form.frontage_depth.data)
            merchant.additional_space_information = form.additional_space_information.data
            merchant.electricity_request = form.electricity_request.data
            merchant.vehicle_length = int(form.vehicle_length.data)
            merchant.vehicle_license_plate = form.vehicle_license_plate.data
            merchant.vehicle_state = form.vehicle_state.data
            merchant.trailer_length = int(form.trailer_length.data)
            merchant.trailer_license_plate = form.trailer_license_plate.data
            merchant.trailer_state = form.trailer_state.data
            merchant.notes = form.notes.data
            merchant.space_fee = int(form.frontage_width.data) * int(form.frontage_depth.data) * .10
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


        db.session.add(merchant)
        db.session.commit()

        send_merchant_confirmation_email(merchant.email,merchant)
        flash('Merchant Application {} created for {}.'.format(
        merchant.id, merchant.business_name))

        return redirect(url_for('merchant.success'))
    elif request.method == 'POST' and not form.validate_on_submit():
        print(request.form)
        form.fname.data = request.form.get('fname')
        form.lname.data = request.form.get('lname')
    return render_template('create_merchant.html', form=form)

@bp.route('/success')
def success():
    return render_template('merchant_success.html')

# @bp.route('/markduplicate', methods=('GET', 'POST'))
# def duplicate():
#     regid = request.args.get('regid')
#     regids = []

#     reg = get_reg(regid)
#     reg.duplicate = True
#     db.session.commit()

#     if current_user.event_id:
#         all_regs = Registrations.query.filter(and_(Registrations.invoice_number == None, Registrations.prereg == True, Registrations.duplicate == False, Registrations.event_id == current_user.event_id)).order_by(Registrations.invoice_email).all()
#     else:
#         all_regs = Registrations.query.filter(and_(Registrations.invoice_number == None, Registrations.prereg == True, Registrations.duplicate == False)).order_by(Registrations.invoice_email).all()

#     for r in all_regs:
#         regids.append(r.id)
        
#     if len(regids) == 0:
#         return redirect(url_for('invoices.unsent'))

#     return redirect(url_for('invoices.createinvoice', regids=[regids]))

# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# @roles_accepted('Admin','Troll Shift Lead','Troll User','Department Head')
# def createatd():
#     form = CreateRegForm()
#     form.lodging.choices = get_lodging_choices()
#     form.kingdom.choices = get_kingdom_choices()
#     if form.validate_on_submit():

#         reg = Registrations(
#         fname = form.fname.data,
#         lname = form.lname.data,
#         scaname = form.scaname.data,
#         age = form.age.data,
#         mbr = True if form.mbr.data == 'Member' else False,
#         mbr_num = form.mbr_num.data,
#         mbr_num_exp = form.mbr_num_exp.data,
#         city = form.city.data,
#         state_province = form.state_province.data,
#         zip = form.zip.data,
#         country = form.country.data,
#         phone = form.phone.data,
#         email = form.email.data,
#         invoice_email = form.invoice_email.data,
#         emergency_contact_name = form.emergency_contact_name.data, 
#         emergency_contact_phone = form.emergency_contact_phone.data,)

#         reg.expected_arrival_date = datetime.now().date()
#         reg.actual_arrival_date = datetime.now().date()
#         registration_price, nmr_price = get_atd_pricesheet_day(reg.actual_arrival_date)
#         reg.registration_price = registration_price
#         reg.registration_balance = registration_price
#         if reg.mbr != True:
#             reg.nmr_price = nmr_price
#             reg.nmr_balance = nmr_price
#         else:
#             reg.nmr_price = 0
#             reg.nmr_balance = 0
        
#         reg.paypal_donation = 0
#         reg.paypal_donation_balance = 0
        
#         reg.balance = reg.registration_price + reg.nmr_price + reg.paypal_donation

#         if form.kingdom.data == '-':
#             flash('Please select a Kingdom.','error')
#             return render_template('create.html', title = 'New Registration', form=form)
#         else:
#             reg.kingdom_id = form.kingdom.data

#         if form.lodging.data == '-':
#             flash('Please select a Camping Group.','error')
#             return render_template('create.html', title = 'New Registration', form=form)
#         else:
#             reg.lodging_id = form.lodging.data

#         if form.mbr.data == 'Member':
#             if datetime.strptime(request.form.get('mbr_num_exp'),'%Y-%m-%d').date() < datetime.now().date():
#                 flash('Membership Expiration Date {} is not current.'.format(form.mbr_num_exp.data),'error')
#                 return render_template('create.html', title = 'New Registration', form=form)

#         db.session.add(reg)
#         db.session.commit()

#         log_reg_action(reg, 'CREATE')

#         flash('Registration {} created for {} {}.'.format(
#             reg.id, reg.fname, reg.lname))

#         return redirect(url_for('troll.reg', regid=reg.id))
#     return render_template('create.html', form=form)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', 'Troll Shift Lead','Department Head')
def editreg():
    regid = request.args['regid']
    reg = get_reg(regid)

    form = EditForm(

        regid = reg.id,
        fname = reg.fname,
        lname = reg.lname,
        scaname = reg.scaname,
        city = reg.city,
        state_province = reg.state_province,
        zip = reg.zip,
        country = reg.country,
        phone = reg.phone,
        email = reg.email,
        invoice_email = reg.invoice_email,
        kingdom = reg.kingdom_id,
        lodging = reg.lodging_id,
        age = reg.age,
        expected_arrival_date = reg.expected_arrival_date,
        mbr = 'Member' if reg.mbr else 'Non-Member',
        medallion = reg.medallion,
        total_due = reg.total_due,
        paypal_donation = reg.paypal_donation,
        prereg = reg.prereg,
        early_on = reg.early_on,
        mbr_num = reg.mbr_num,
        mbr_num_exp = reg.mbr_num_exp if reg.mbr_num_exp is not None else None,
        emergency_contact_name = reg.emergency_contact_name,
        emergency_contact_phone = reg.emergency_contact_phone,
        notes = reg.notes
    )

    form.lodging.choices = get_lodging_choices()
    form.kingdom.choices = get_kingdom_choices()

    if request.method == 'POST':

        if current_user.has_role('Troll Shift Lead'):
            reg.notes = request.form.get('notes')
            if request.form.get('medallion') != '' and request.form.get('medallion') != None:
                medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()
            else:
                medallion_check = None

            if medallion_check is not None and int(regid) != int(medallion_check.id):
                flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.id),'error')
                dup_url = '<a href=' + url_for('troll.reg', regid=str(medallion_check.id)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
                flash(Markup(dup_url),'error')
            else:
                if request.form.get('medallion'):
                    reg.medallion = int(request.form.get('medallion'))
                else: reg.medallion = None

                reg.mbr = request.form.get('mbr')
                if request.form.get('mbr_num'):
                    reg.mbr_num = int(request.form.get('mbr_num'))
                else: reg.mbr_num = None

                if request.form.get('mbr_num_exp'):
                    reg.mbr_num_exp = request.form.get('mbr_num_exp')

                db.session.commit()

                log_reg_action(reg, 'EDIT')

                return redirect(url_for('troll.reg',regid=regid))
            
        else:

            reg.notes = request.form.get('notes')

            if request.form.get('medallion') != '' and request.form.get('medallion') != None:
                medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()
            else:
                medallion_check = None

            if medallion_check is not None and int(regid) != int(medallion_check.id):
                flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.id),'error')
                dup_url = '<a href=' + url_for('troll.reg', regid=str(medallion_check.id)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
                flash(Markup(dup_url),'error')

            else:
                reg.fname = request.form.get('fname')
                reg.lname = request.form.get('lname')
                reg.scaname = request.form.get('scaname')
                reg.city = request.form.get('city')
                reg.state_province = request.form.get('state_province')
                if request.form.get('zip'):
                    reg.zip = int(request.form.get('zip'))
                else: reg.zip = None
                reg.country = request.form.get('country')
                reg.phone = request.form.get('phone')
                reg.email = request.form.get('email')
                reg.invoice_email = request.form.get('invoice_email')
                reg.kingdom = request.form.get('kingdom')
                reg.lodging = request.form.get('lodging')
                reg.expected_arrival_date = datetime.strptime(request.form.get('expected_arrival_date'), '%Y-%m-%d') if (request.form.get('expected_arrival_date') != '' and request.form.get('expected_arrival_date')) else None
                reg.age = request.form.get('age')
                reg.mbr = request.form.get('mbr')
                if request.form.get('medallion'):
                    reg.medallion = int(request.form.get('medallion'))
                else: reg.medallion = None
                if request.form.get('atd_paid'):
                    reg.atd_paid = int(request.form.get('atd_paid'))
                else: reg.atd_paid = 0
                if request.form.get('price_paid'):
                    reg.price_paid = int(request.form.get('price_paid'))
                else: reg.price_paid =  0
                if request.form.get('pay_type') == '' or request.form.get('pay_type') == None:
                    reg.atd_pay_type = None
                else: reg.atd_pay_type = request.form.get('pay_type')
                if request.form.get('price_calc'):
                    reg.price_calc = int(request.form.get('price_calc'))
                else: reg.price_calc = 0
                if request.form.get('price_due'):
                    reg.price_due = int(request.form.get('price_due'))
                else: reg.price_due = 0
                reg.paypal_donation = bool(request.form.get('paypal_donation'))
                if request.form.get('paypal_donation_amount'):
                    reg.paypal_donation_amount = int(request.form.get('paypal_donation_amount'))
                else: reg.paypal_donation_amount = 0
                reg.prereg = request.form.get('prereg')
                reg.early_on = bool(request.form.get('early_on'))
                if request.form.get('mbr_num'):
                    reg.mbr_num = int(request.form.get('mbr_num'))
                else: reg.mbr_num = None
                if request.form.get('mbr_num_exp'):
                    reg.mbr_num_exp = request.form.get('mbr_num_exp')
                reg.emergency_contact_name = request.form.get('emergency_contact_name')
                reg.emergency_contact_phone = request.form.get('emergency_contact_phone') 

                reg.price_due = (reg.price_calc + reg.paypal_donation_amount) - (reg.price_paid + reg.atd_paid)
                if reg.price_due < 0:  #Account for people who showed up late.  No refund.
                    reg.price_due = 0

                db.session.commit()

                log_reg_action(reg, 'EDIT')

                return redirect(url_for('troll.reg',regid=regid))

    return render_template('editreg.html', regid=reg.id, reg=reg, form=form)