from flask import render_template
from app.registration import bp

from flask_login import current_user, login_required
from flask import render_template, request, url_for, flash, redirect
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from app.utils.email_utils import *

from flask_security import roles_accepted
from markupsafe import Markup

def create_prereg(data):
    reg = Registrations(
        fname = data.fname.data,
        lname = data.lname.data,
        scaname = data.scaname.data,
        city = data.city.data,
        state_province = data.state_province.data,
        zip = data.zip.data,
        country = data.country.data,
        phone = data.phone.data, 
        email = data.email.data, 
        invoice_email = data.invoice_email.data,
        age = data.age.data,
        kingdom = data.kingdom.data,
        emergency_contact_name = data.emergency_contact_name.data, 
        emergency_contact_phone = data.emergency_contact_phone.data, 
        lodging = data.lodging.data, 
        mbr = True if data.mbr.data == 'Member' else False,
        mbr_num_exp = datetime.strftime(data.mbr_num_exp.data, '%Y-%m-%d') if data.mbr_num_exp.data is not None else None, 
        mbr_num = data.mbr_num.data,
        prereg = True,
        prereg_date_time = datetime.now().replace(microsecond=0).isoformat(),
        paypal_donation = 3 if data.paypal_donation.data == True else 0,
        paypal_donation_balance = 3 if data.paypal_donation.data == True else 0,
        royal_departure_date = data.royal_departure_date.data,
        royal_title = data.royal_title.data if data.royal_title.data != '' else None
    )

    if data.expected_arrival_date.data == 'Early_On':
        reg.early_on = True
        reg.expected_arrival_date = datetime.strptime('03-08-2025', '%m-%d-%Y')
    else:
        reg.expected_arrival_date = datetime.strptime(data.expected_arrival_date.data, '%m-%d-%Y')

    if data.age.data == '18+':
        registration_price, nmr_price = get_prereg_pricesheet_day(reg.expected_arrival_date)
        reg.registration_price = registration_price
        reg.registration_balance = registration_price
        if not reg.mbr:
            reg.nmr_price = nmr_price
            reg.nmr_balance = nmr_price
        else:
            reg.nmr_price = 0
            reg.nmr_balance = 0
    
        reg.balance = reg.registration_balance + reg.nmr_balance + reg.paypal_donation_balance

    return reg

def JSONtoDict(string_data):
    data_dict = {}
    pairs = string_data.replace('{','').replace('}','').replace('"','').split(', ')
    for pair in pairs:
        new_pair = pair.split(': ')
        data_dict[new_pair[0]] = new_pair[1]
    return data_dict

def DicttoReg(dict):
    reg = Registrations(
        fname = dict['fname'],
        lname = dict['lname'],
        scaname = dict['scaname'],
        city = dict['city'],
        state_province = dict['state_province'],
        zip = int(dict['zip']),
        country = dict['country'],
        phone = dict['phone'],  
        email = dict['email'],  
        invoice_email = dict['invoice_email'],
        age = dict['age'],
        kingdom = dict['kingdom'],
        emergency_contact_name = dict['emergency_contact_name'],  
        emergency_contact_phone = dict['emergency_contact_phone'],  
        lodging = dict['lodging'], 
        mbr = bool(dict['mbr']),
        mbr_num_exp = dict['mbr_num_exp'] if dict['mbr_num_exp'] != 'null' else None, 
        mbr_num = int(dict['mbr_num']) if dict['mbr_num'] != 'null' else None,
        prereg = bool(dict['prereg']),
        prereg_date_time = dict['prereg_date_time'],
        paypal_donation = int(dict['paypal_donation']),
        paypal_donation_balance = int(dict['paypal_donation_balance']),
        royal_departure_date = dict['royal_departure_date'] if dict['royal_departure_date'] != 'null' else None,
        royal_title = dict['royal_title'] if dict['royal_title'] != 'null' else None,
        expected_arrival_date = dict['expected_arrival_date']
    )

    if dict['expected_arrival_date'] == 'Early_On':
        reg.early_on = True
        reg.expected_arrival_date = datetime.strptime('03-08-2025', '%Y-%m-%d')
    else:
        reg.expected_arrival_date = datetime.strptime(dict['expected_arrival_date'], '%Y-%m-%d')

    if dict['age'] == '18+':
        registration_price, nmr_price = get_prereg_pricesheet_day(reg.expected_arrival_date)
        reg.registration_price = registration_price
        reg.registration_balance = registration_price
        if not reg.mbr:
            reg.nmr_price = nmr_price
            reg.nmr_balance = nmr_price
        else:
            reg.nmr_price = 0
            reg.nmr_balance = 0
    
        reg.balance = reg.registration_balance + reg.nmr_balance + reg.paypal_donation_balance

    return reg
        

@bp.route('/', methods=('GET', 'POST'))
def createprereg():
    # Close Pre-Reg at Midnight 02/22/2025
    # if datetime.now().date() >= datetime.strptime('02/22/2025','%m/%d/%Y').date():
    #     return render_template("prereg_closed.html")

    form = CreatePreRegForm()
    loading_df = pd.read_csv('gwlodging.csv')
    lodgingdata = loading_df.to_dict(orient='list')
    form.lodging.choices = lodgingdata

    if form.validate_on_submit() and request.method == 'POST':
        
        if request.form.get("action") == 'Submit_Another':
            additional_registrations = []
            reg_names = []
            print(request.form.keys())
            if 'additional_registration-1' in request.form.keys():
                for key in request.form.keys():
                    if 'additional_registration' in key:
                        reg_names.append(JSONtoDict(request.form.get(key)))
                        additional_registrations.append(request.form.get(key))
            new_reg = create_prereg(form)
            additional_registrations.append(new_reg.toJSON())
            reg_names.append(new_reg)
            return render_template('create_prereg.html', form=form, additional_registrations=additional_registrations, reg_names=reg_names)
            # return redirect(url_for('registration.createprereg', form=form, additional_registrations=additional_registrations, reg_names=reg_names))
        else:
            additional_registrations = []
            if 'additional_registration-1' in request.form.keys():
                for key in request.form.keys():
                    if 'additional_registration' in key:
                        additional_registrations.append(DicttoReg(JSONtoDict(request.form.get(key))))
                        
            for add_reg in additional_registrations:
                db.session.add(add_reg)

            reg = create_prereg(form)

            db.session.add(reg)
            db.session.commit()

            for add_reg in additional_registrations:
                # send_confirmation_email(add_reg.email,add_reg)
                flash('Registration {} created for {} {}.'.format(
                add_reg.id, add_reg.fname, add_reg.lname))
            # send_confirmation_email(reg.email,reg)
            flash('Registration {} created for {} {}.'.format(
            reg.id, reg.fname, reg.lname))


            return redirect(url_for('registration.success'))
    return render_template('create_prereg.html', form=form)

@bp.route('/success')
def success():
    return render_template('reg_success.html')

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Troll Shift Lead','Troll User','Department Head')
def createatd():
    form = CreateRegForm()
    if form.validate_on_submit():

        reg = Registrations(
        fname = form.fname.data,
        lname = form.lname.data,
        scaname = form.scaname.data,
        kingdom = form.kingdom.data,
        lodging = form.lodging.data,
        age = form.age.data,
        mbr = True if form.mbr.data == 'Member' else False,
        mbr_num = form.mbr_num.data,
        mbr_num_exp = form.mbr_num_exp.data,
        city = form.city.data,
        state_province = form.state_province.data,
        zip = form.zip.data,
        country = form.country.data,
        phone = form.phone.data,
        email = form.email.data,
        invoice_email = form.invoice_email.data,
        emergency_contact_name = form.emergency_contact_name.data, 
        emergency_contact_phone = form.emergency_contact_phone.data,)
        reg.expected_arrival_date = datetime.now().date()
        reg.actual_arrival_date = datetime.now().date()
        registration_price, nmr_price = get_atd_pricesheet_day(reg.actual_arrival_date)
        reg.registration_price = registration_price
        reg.registration_balance = registration_price
        if reg.mbr != True:
            reg.nmr_price = nmr_price
            reg.nmr_balance = nmr_price
        else:
            reg.nmr_price = 0
            reg.nmr_balance = 0
        
        reg.paypal_donation = 0
        reg.paypal_donation_balance = 0
        
        reg.balance = reg.registration_price + reg.nmr_price + reg.paypal_donation

        if form.mbr.data == 'Member':
            if datetime.strptime(request.form.get('mbr_num_exp'),'%Y-%m-%d').date() < datetime.now().date():
                flash('Membership Expiration Date {} is not current.'.format(form.mbr_num_exp.data),'error')
                return render_template('create.html', title = 'New Registration', form=form)

        db.session.add(reg)
        db.session.commit()

        log_reg_action(reg, 'CREATE')


        flash('Registration {} created for {} {}.'.format(
            reg.id, reg.fname, reg.lname))

        return redirect(url_for('troll.reg', regid=reg.id))
    return render_template('create.html', form=form)

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
        kingdom = reg.kingdom,
        lodging = reg.lodging,
        age = reg.age,
        mbr = reg.mbr,
        medallion = reg.medallion,
        atd_paid = reg.atd_paid,
        price_paid = reg.price_paid,
        pay_type = reg.atd_pay_type,
        price_calc = reg.price_calc,
        price_due = reg.price_due,
        paypal_donation = reg.paypal_donation,
        paypal_donation_amount = reg.paypal_donation_amount,
        prereg = reg.prereg,
        early_on =reg.early_on,
        mbr_num = reg.mbr_num,
        mbr_num_exp = datetime.strptime(reg.mbr_num_exp, '%Y-%m-%d') if reg.mbr_num_exp is not None else None,
        emergency_contact_name = reg.emergency_contact_name,
        emergency_contact_phone = reg.emergency_contact_phone,
        notes = reg.notes
    )

    if reg.expected_arrival_date != None:
        try:
            form.expected_arrival_date.data = datetime.strptime(reg.expected_arrival_date, '%Y-%m-%d %H:%M:%S')
        except:
            form.expected_arrival_date.data = datetime.strptime(reg.expected_arrival_date, "%m-%d-%Y")

    loading_df = pd.read_csv('gwlodging.csv')
    lodgingdata = loading_df.to_dict(orient='list')
    form.lodging.choices = lodgingdata

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