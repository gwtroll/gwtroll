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

def JSONtoDict(string_data):
    data_dict = {}
    pairs = string_data.replace('{','').replace('}','').replace('"','').split(', ')
    for pair in pairs:
        new_pair = pair.split(': ')
        data_dict[new_pair[0]] = new_pair[1]
    return data_dict

def DicttoReg(dict):
    reg = Registrations()
    for field in dir(reg):
        if field in dict:
            if field in ['balance','mbr_num','zip','registration_price','nmr_price','paypal_donation','registration_balance','nmr_balance','paypal_donation_balance']: 
                reg.__dict__[field] = int(dict[field])
            elif field in ['mbr','prereg']: 
                reg.__dict__[field] = True if dict[field] == 'true' else False
            else:
                reg.__dict__[field] = dict[field]
    # reg = Registrations(
    #     fname = dict['fname'],
    #     lname = dict['lname'],
    #     scaname = dict['scaname'],
    #     city = dict['city'],
    #     state_province = dict['state_province'],
    #     zip = int(dict['zip']),
    #     country = dict['country'],
    #     phone = dict['phone'],  
    #     email = dict['email'].lower(),  
    #     invoice_email = dict['invoice_email'].lower(),
    #     age = dict['age'],
    #     kingdom_id = int(dict['kingdom_id']),
    #     emergency_contact_name = dict['emergency_contact_name'],  
    #     emergency_contact_phone = dict['emergency_contact_phone'],  
    #     lodging_id = int(dict['lodging_id']), 
    #     mbr = True if dict['mbr'] == 'true' or dict['mbr'] == True else False,
    #     mbr_num_exp = dict['mbr_num_exp'] if dict['mbr_num_exp'] != 'null' else None, 
    #     mbr_num = int(dict['mbr_num']) if dict['mbr_num'] != 'null' else None,
    #     prereg = True,
    #     paypal_donation = int(dict['paypal_donation']),
    #     paypal_donation_balance = int(dict['paypal_donation_balance']),
    #     royal_departure_date = dict['royal_departure_date'] if dict['royal_departure_date'] != 'null' else None,
    #     royal_title = dict['royal_title'] if dict['royal_title'] != 'null' else None,
    # )
    
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
    return redirect(url_for('registration.createprereg'))

@bp.route('/', methods=('GET', 'POST'))
def createprereg():

    event = EventVariables.query.first()
    event_dates = pd.date_range(start=event.start_date, end=event.end_date).tolist()
    pricesheet = PriceSheet.query.filter(PriceSheet.arrival_date.in_(event_dates)).order_by(PriceSheet.arrival_date).all()
    # Close Pre-Reg at Midnight 02/22/2025
    ### UNCOMMENT
    # if datetime.now(pytz.timezone('America/Chicago')).date() <= event.preregistration_open_date:
    #     return render_template("prereg_closed.html", event=event,pricesheet=pricesheet)
    if datetime.now(pytz.timezone('America/Chicago')).date() >= event.preregistration_close_date:
        return render_template("prereg_closed.html", event=event,pricesheet=pricesheet)
    invoice_totals = {'registration':0, 'nmr':0, 'donation':0, 'total':0}

    form = CreatePreRegForm()
    form.lodging.choices = get_lodging_choices()
    form.kingdom.choices = get_kingdom_choices()
    form.expected_arrival_date.choices = get_reg_arrival_dates()

    if 'additional_registrations' in session and len(session['additional_registrations']) > 0:
        additional_registrations = [json.loads(r) for r in session['additional_registrations']]
        form.invoice_email.data = additional_registrations[0]['invoice_email']
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

            new_reg = Registrations()
            form.populate_object(new_reg)
            if 'additional_registrations' not in session:
                session['additional_registrations'] = []
            reg_list = session['additional_registrations']
            reg_json = new_reg.toJSON()

            reg_list.append(reg_json)
            session['additional_registrations'] = reg_list
            additional_registrations = [json.loads(r) for r in session['additional_registrations']]
 
            for ar in additional_registrations:
                invoice_totals['registration'] += int(ar['registration_price'])
                invoice_totals['nmr'] += int(ar['nmr_price'])
                invoice_totals['donation'] += int(ar['paypal_donation'])
                invoice_totals['total'] += (int(ar['registration_price']) + int(ar['nmr_price']) + int(ar['paypal_donation']))


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

            reg = Registrations()
            form.populate_object(reg)

            db.session.add(reg)
            db.session.commit()
            if 'additional_registrations' in session:
                del session['additional_registrations']

            flash_string = ''
            for add_reg in additional_registrations:
                send_confirmation_email(add_reg.email,add_reg)
                if add_reg.balance<=0:
                    send_fastpass_email(add_reg.email,add_reg)
                flash_string += ('\nRegistration {} created for {} {}.'.format(add_reg.id, add_reg.fname, add_reg.lname))
            send_confirmation_email(reg.email,reg)
            if reg.balance<=0:
                    send_fastpass_email(reg.email,reg)
            flash_string += 'Registration {} created for {} {}.'.format(reg.id, reg.fname, reg.lname)
            flash(flash_string)
            return redirect(url_for('registration.success'))

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

    all_regs = Registrations.query.filter(and_(Registrations.invoices == None, Registrations.prereg == True, Registrations.duplicate == False, Registrations.invoice_email==reg.invoice_email, Registrations.balance > 0)).order_by(Registrations.invoice_email).all()

    for r in all_regs:
        regids.append(r.id)
        
    if len(regids) == 0:
        return redirect(url_for('invoices.unsent'))

    return redirect(url_for('invoices.createinvoice', regids=[regids], type="REGISTRATION"))

@bp.route('/atd', methods=('GET', 'POST'))
@login_required
@permission_required('troll')
def createatd():
    form = CreateRegForm()
    form.lodging.choices = get_lodging_choices()
    form.kingdom.choices = get_kingdom_choices()
    if request.method == 'POST' and form.validate_on_submit():
        if form.mbr.data == 'Member':
            if datetime.strptime(request.form.get('mbr_num_exp'),'%Y-%m-%d').date() < datetime.now(pytz.timezone('America/Chicago')).date():
                flash('Membership Expiration Date {} is not current.'.format(form.mbr_num_exp.data),'error')
                return render_template('create.html', title = 'New Registration', form=form)

        reg = Registrations()
        form.populate_object(reg)

        db.session.add(reg)
        db.session.commit()

        flash('Registration {} created for {} {}.'.format(
            reg.id, reg.fname, reg.lname))

        return redirect(url_for('troll.waiver', regid=reg.id))
    return render_template('create.html', form=form)

@bp.route('/<int:regid>', methods=['GET', ''])
@login_required
@permission_required('registration_view')
def viewreg(regid):
    reg = get_reg(regid)
    return render_template('viewreg.html', reg=reg)

@bp.route('/<int:regid>/edit_limited', methods=['GET', 'POST'])
@login_required
@permission_required('registration_edit_limited')
def editreg_limited(regid):
    reg = get_reg(regid)

    form = EditLimitedForm()

    if request.method == 'POST':
        reg.notes = request.form.get('notes')
        if request.form.get('medallion') != '' and request.form.get('medallion') != None:
            medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()

        if medallion_check is not None and int(regid) != int(medallion_check.id):
            flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.id),'error')
            dup_url = '<a href=' + url_for('troll.reg', regid=str(medallion_check.id)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
            flash(Markup(dup_url),'error')
            return render_template('editreg_limited.html', reg=reg, form=form)
        
        form.populate_object(reg)

        db.session.commit()

        return redirect(url_for('troll.reg',regid=reg.id))
    else:
        form.populate_form(reg)

    return render_template('editreg_limited.html', reg=reg, form=form)

@bp.route('/<int:regid>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('registration_edit')
def editreg(regid):
    reg = get_reg(regid)

    form = EditForm()
    form.lodging.choices = get_lodging_choices()
    form.kingdom.choices = get_kingdom_choices()

    if request.method == 'POST' and form.validate_on_submit():
        medallion_check = None
        if form.medallion.data != '' and form.medallion.data != None:
            medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()

        if medallion_check is not None and int(regid) != int(medallion_check.id):
            dup_url = '<a href=' + url_for('troll.reg', regid=str(medallion_check.id)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
            flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.id) + ": " + Markup(dup_url),'error')
            form.populate_form(reg)
            return render_template('editreg.html', regid=reg.id, reg=reg, form=form)

        form.populate_object(reg)
        db.session.commit()
        return redirect(url_for('troll.reg',regid=regid))

    form.populate_form(reg)
    return render_template('editreg.html', regid=reg.id, reg=reg, form=form)