from flask import render_template
from app.registration import bp

from flask_login import current_user, login_required
from flask import render_template, request, url_for, flash, redirect, session
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from app.utils.email_utils import *
from app.utils.security_utils import *
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
        email = (data.email.data).lower(), 
        invoice_email = (data.invoice_email.data).lower(),
        age = data.age.data,
        kingdom_id = data.kingdom.data,
        emergency_contact_name = data.emergency_contact_name.data, 
        emergency_contact_phone = data.emergency_contact_phone.data, 
        lodging_id = data.lodging.data, 
        mbr = True if data.mbr.data == 'Member' else False,
        mbr_num_exp = datetime.strftime(data.mbr_num_exp.data, '%Y-%m-%d') if data.mbr_num_exp.data is not None else None, 
        mbr_num = data.mbr_num.data,
        prereg = True,
        prereg_date_time = datetime.now().replace(microsecond=0).isoformat(),
        paypal_donation = int(data.paypal_donation_amount.data) if data.paypal_donation.data == True else 0,
        paypal_donation_balance = int(data.paypal_donation_amount.data) if data.paypal_donation.data == True else 0,
        royal_departure_date = data.royal_departure_date.data,
        royal_title = data.royal_title.data if data.royal_title.data != '' else None
    )

    reg.expected_arrival_date = datetime.strptime(data.expected_arrival_date.data, '%Y-%m-%d')

    if data.age.data == '18+':
        registration_price = get_prereg_pricesheet_day(reg.expected_arrival_date)
        reg.registration_price = registration_price
        reg.registration_balance = registration_price
        if not reg.mbr:
            reg.nmr_price = 10
            reg.nmr_balance = 10
        else:
            reg.nmr_price = 0
            reg.nmr_balance = 0
    else:
        reg.registration_price = 0
        reg.registration_balance = 0
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
        email = dict['email'].lower(),  
        invoice_email = dict['invoice_email'].lower(),
        age = dict['age'],
        kingdom_id = dict['kingdom_id'],
        emergency_contact_name = dict['emergency_contact_name'],  
        emergency_contact_phone = dict['emergency_contact_phone'],  
        lodging_id = dict['lodging_id'], 
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

    reg.expected_arrival_date = datetime.strptime(dict['expected_arrival_date'], '%Y-%m-%d')

    if dict['age'] == '18+':
        registration_price = get_prereg_pricesheet_day(reg.expected_arrival_date)
        reg.registration_price = registration_price
        reg.registration_balance = registration_price
        if not reg.mbr:
            reg.nmr_price = 10
            reg.nmr_balance = 10
        else:
            reg.nmr_price = 0
            reg.nmr_balance = 0
    
        reg.balance = reg.registration_balance + reg.nmr_balance + reg.paypal_donation_balance

    return reg

@bp.route('/removeregistration/<int:index>', methods=('GET', 'POST'))
def removeregistration(index):
    reg_list = session['additional_registrations']
    new_list = []
    del reg_list[index]
    for r in reg_list:
        new_list.append(json.loads(r))
    session['additional_registrations'] = reg_list
    print(session['additional_registrations'])
    return redirect(url_for('registration.createprereg'))

@bp.route('/', methods=('GET', 'POST'))
def createprereg():

    event = EventVariables.query.first()
    # Close Pre-Reg at Midnight 02/22/2025
    if datetime.now().date() >= event.preregistration_close_date:
        return render_template("prereg_closed.html", event=event)
    invoice_totals = {'registration':0, 'nmr':0, 'donation':0, 'total':0}

    form = CreatePreRegForm()
    form.lodging.choices = get_lodging_choices()
    form.kingdom.choices = get_kingdom_choices()
    form.expected_arrival_date.choices = get_reg_arrival_dates()
    event_dates = pd.date_range(start=event.start_date, end=event.end_date).tolist()
    pricesheet = PriceSheet.query.filter(PriceSheet.arrival_date.in_(event_dates)).order_by(PriceSheet.arrival_date).all()
    print(pricesheet)
    if 'additional_registrations' in session and len(session['additional_registrations']) > 0:
        additional_registrations = [json.loads(r) for r in session['additional_registrations']]
        form.invoice_email.data = additional_registrations[0]['invoice_email']
        for ar in additional_registrations:
            invoice_totals['registration'] += ar['registration_price']
            invoice_totals['nmr'] += ar['nmr_price']
            invoice_totals['donation'] += ar['paypal_donation']
            invoice_totals['total'] += (ar['registration_price'] + ar['nmr_price'] + ar['paypal_donation'])
    else:
        additional_registrations = []

    merchantid = request.args.get('merchantid')
    if merchantid is not None and request.form.get("action") == None:
        merchant = Merchant.query.filter_by(id=merchantid).first()
        if merchant is None:
            flash('Merchant not found.','error')
            return redirect(url_for('registration.createprereg'))
        else:
            form.fname.data = merchant.fname
            form.lname.data = merchant.lname
            form.scaname.data = merchant.sca_name
            form.email.data = merchant.email
            form.invoice_email.data = merchant.email
            form.phone.data = merchant.phone
            form.city.data = merchant.city
            form.state_province.data = merchant.state_province
            form.zip.data = merchant.zip

    if form.validate_on_submit() and request.method == 'POST':

        if request.form.get("action") == 'Submit_Another':

            new_reg = create_prereg(form)
            if 'additional_registrations' not in session:
                session['additional_registrations'] = []
            reg_list = session['additional_registrations']
            reg_json = new_reg.toJSON()
            # if reg_json in reg_list:
            #     flash('Duplicate Registration Prevented')
            #     return render_template('create_prereg.html', form=form, additional_registrations=additional_registrations, clear=True, pricesheet=pricesheet, event=event)

            reg_list.append(reg_json)
            session['additional_registrations'] = reg_list
            additional_registrations = [json.loads(r) for r in session['additional_registrations']]
 
            form.fname.data = None
            form.lname.data = None
            form.scaname.data = None
            form.email.data = None
            form.phone.data = None
            form.city.data = None
            form.state_province.data = None
            form.zip.data = None
            return render_template('create_prereg.html', form=form, additional_registrations=additional_registrations, clear=True, pricesheet=pricesheet, event=event, invoice_totals=invoice_totals)
        else:
            additional_registrations = []

            if 'additional_registrations' in session:
                for r in session['additional_registrations']:
                    add_reg = DicttoReg(JSONtoDict(r))
                    additional_registrations.append(add_reg)
                    db.session.add(add_reg)

            reg = create_prereg(form)

            db.session.add(reg)
            db.session.commit()
            if 'additional_registrations' in session:
                del session['additional_registrations']

            for add_reg in additional_registrations:
                send_confirmation_email(add_reg.email,add_reg)
                flash('Registration {} created for {} {}.'.format(
                add_reg.id, add_reg.fname, add_reg.lname))
            send_confirmation_email(reg.email,reg)
            flash('Registration {} created for {} {}.'.format(
            reg.id, reg.fname, reg.lname))
            return redirect(url_for('registration.success'))
    # elif request.method == 'POST' and not form.validate_on_submit():
    #     print(request.form)
    #     form.fname.data = request.form.get('fname')
    #     form.lname.data = request.form.get('lname')
    return render_template('create_prereg.html', form=form, pricesheet=pricesheet, additional_registrations=additional_registrations, event=event, clear=False, invoice_totals=invoice_totals)

@bp.route('/success')
def success():
    return render_template('reg_success.html')

@bp.route('/markduplicate', methods=('GET', 'POST'))
@login_required
@permission_required('registration_edit')
def duplicate():
    regid = request.args.get('regid')
    regids = []

    reg = get_reg(regid)
    reg.duplicate = True
    db.session.commit()

    all_regs = Registrations.query.filter(and_(Registrations.invoice_number == None, Registrations.prereg == True, Registrations.duplicate == False, Registrations.invoice_email==reg.invoice_email, Registrations.balance > 0)).order_by(Registrations.invoice_email).all()

    for r in all_regs:
        regids.append(r.id)
        
    if len(regids) == 0:
        return redirect(url_for('invoices.unsent'))

    return redirect(url_for('invoices.createinvoice', regids=[regids], type="REGISTRATION"))

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@permission_required('registration_edit')
def createatd():
    form = CreateRegForm()
    form.lodging.choices = get_lodging_choices()
    form.kingdom.choices = get_kingdom_choices()
    if form.validate_on_submit():

        reg = Registrations(
        fname = form.fname.data,
        lname = form.lname.data,
        scaname = form.scaname.data,
        age = form.age.data,
        mbr = True if form.mbr.data == 'Member' else False,
        mbr_num = form.mbr_num.data,
        mbr_num_exp = form.mbr_num_exp.data,
        phone = form.phone.data,
        email = form.email.data,
        zip = form.zip.data,
        emergency_contact_name = form.emergency_contact_name.data, 
        emergency_contact_phone = form.emergency_contact_phone.data,)

        reg.expected_arrival_date = datetime.now().date()
        reg.actual_arrival_date = datetime.now().date()

        if reg.age == '18+':
            registration_price = get_atd_pricesheet_day(reg.actual_arrival_date)
            reg.registration_price = registration_price
            reg.registration_balance = registration_price
            if reg.mbr != True:
                reg.nmr_price = 10
                reg.nmr_balance = 10
            else:
                reg.nmr_price = 0
                reg.nmr_balance = 0
        else:
            reg.registration_price = 0
            reg.registration_balance = 0
            reg.nmr_price = 0
            reg.nmr_balance = 0
            
        reg.paypal_donation = 0
        reg.paypal_donation_balance = 0
        
        reg.balance = reg.registration_price + reg.nmr_price + reg.paypal_donation

        reg.kingdom_id = form.kingdom.data
        reg.lodging_id = form.lodging.data

        if form.mbr.data == 'Member':
            if datetime.strptime(request.form.get('mbr_num_exp'),'%Y-%m-%d').date() < datetime.now().date():
                flash('Membership Expiration Date {} is not current.'.format(form.mbr_num_exp.data),'error')
                return render_template('create.html', title = 'New Registration', form=form)

        db.session.add(reg)
        db.session.commit()

        log_reg_action(reg, 'CREATE')

        flash('Registration {} created for {} {}.'.format(
            reg.id, reg.fname, reg.lname))

        return redirect(url_for('troll.waiver', regid=reg.id))
    return render_template('create.html', form=form)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
@permission_required('registration_edit')
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
        early_on = reg.early_on_approved,
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