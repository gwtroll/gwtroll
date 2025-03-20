from flask import render_template
from app.registration import bp

from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, url_for, flash, redirect
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted
import json
from markupsafe import Markup


@bp.route('/', methods=('GET', 'POST'))
def createprereg():
    # Close Pre-Reg at Midnight 02/22/2025
    if datetime.now().date() >= datetime.strptime('02/22/2025','%m/%d/%Y').date():
        return render_template("prereg_closed.html")

    form = CreatePreRegForm()

    loading_df = pd.read_csv('gwlodging.csv')
    lodgingdata = loading_df.to_dict(orient='list')
    form.lodging.choices = lodgingdata

    if form.validate_on_submit() and request.method == 'POST':

        reg = Registrations(
            fname = form.fname.data,
            lname = form.lname.data,
            scaname = form.scaname.data,
            city = form.city.data,
            state_province = form.state_province.data,
            zip = form.zip.data,
            country = form.country.data,
            phone = form.phone.data, 
            email = form.email.data, 
            invoice_email = form.invoice_email.data,
            rate_age = form.rate_age.data,
            kingdom = form.kingdom.data, 
            lodging = form.lodging.data, 
            prereg_status = 'SUCCEEDED',
            invoice_status = 'UNSENT',
            rate_mbr = form.rate_mbr.data,
            mbr_num_exp = form.mbr_num_exp.data, 
            mbr_num = form.mbr_num.data,
            onsite_contact_name = form.onsite_contact_name.data, 
            onsite_contact_sca_name = form.onsite_contact_sca_name.data, 
            onsite_contact_kingdom = form.onsite_contact_kingdom.data, 
            onsite_contact_group = form.onsite_contact_group.data, 
            offsite_contact_name = form.offsite_contact_name.data, 
            offsite_contact_phone = form.offsite_contact_phone.data,
            prereg_date_time = datetime.now().replace(microsecond=0).isoformat(),
            paypal_donation = form.paypal_donation.data,
            price_paid = 0,
            atd_paid = 0,
            royal_departure_date = form.royal_departure_date.data,
            royal_title = form.royal_title.data if form.royal_title.data != '' else None
        )

        if form.rate_date.data == 'Early_On':
            reg.early_on = True
            rate_date = '03-08-2025'
            reg.rate_date = datetime.strptime('03-08-2025', '%m-%d-%Y'),
        else:
            rate_date = form.rate_date.data
            reg.rate_date = datetime.strptime(form.rate_date.data, '%m-%d-%Y'),

        if form.rate_age.data != '18+':
            rate_category = 'CHILDREN 17 AND UNDER'
        elif form.rate_mbr.data == 'Member':
            rate_category = 'Pre-Registered Member'
        elif form.rate_mbr.data == 'Non-Member':
            rate_category = 'Pre-Registered Non-Member'

        with open('rate_sheet.json') as f:
            rate_sheet = json.load(f)
            reg.price_calc = rate_sheet[rate_category][rate_date]
            reg.price_due = rate_sheet[rate_category][rate_date]

        if reg.paypal_donation == True:
            reg.paypal_donation_amount = 3
        else:
            reg.paypal_donation_amount = 0

        reg.price_due += reg.paypal_donation_amount

        print(reg.early_on)
        db.session.add(reg)
        db.session.commit()

        regid = reg.regid
        flash('Registration {} created for {} {}.'.format(
            reg.regid, reg.fname, reg.lname))
        
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
        rate_age = form.rate_age.data,
        rate_mbr = form.rate_mbr.data,
        mbr_num = form.mbr_num.data,
        mbr_num_exp = form.mbr_num_exp.data,
        city = form.city.data,
        state_province = form.state_province.data,
        zip = form.zip.data,
        country = form.country.data,
        phone = form.phone.data,
        email = form.email.data,
        invoice_email = form.invoice_email.data,
        onsite_contact_name = form.onsite_contact_name.data, 
        onsite_contact_sca_name = form.onsite_contact_sca_name.data, 
        onsite_contact_kingdom = form.onsite_contact_kingdom.data, 
        onsite_contact_group = form.onsite_contact_group.data, 
        offsite_contact_name = form.offsite_contact_name.data, 
        offsite_contact_phone = form.offsite_contact_phone.data,
        atd_paid = 0,
        price_paid = 0)
        #mbr_num = form.mbr_num.data,
        #mbr_exp = form.mbr_exp.data)
        reg.rate_date = datetime.now().date()
        reg.price_calc = calculate_price_calc(reg)
        if reg.price_paid + reg.atd_paid > reg.price_calc:  #Account for people who showed up late.  No refund.
            reg.price_due = 0
        else:
            reg.price_due = reg.price_calc - (reg.price_paid + reg.atd_paid)

        if form.rate_mbr.data == 'Member':
            if datetime.strptime(request.form.get('mbr_num_exp'),'%Y-%m-%d').date() < datetime.now().date():
                flash('Membership Expiration Date {} is not current.'.format(form.mbr_num_exp.data))
                return render_template('create.html', title = 'New Registration', form=form)

        db.session.add(reg)
        db.session.commit()

        log_reg_action(reg, 'CREATE')


        flash('Registration {} created for {} {}.'.format(
            reg.regid, reg.fname, reg.lname))

        return redirect(url_for('troll.reg', regid=reg.regid))
    return render_template('create.html', form=form)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', 'Troll Shift Lead','Department Head')
def editreg():
    regid = request.args['regid']
    reg = get_reg(regid)

    form = EditForm(
        regid = reg.regid,
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
        rate_age = reg.rate_age,
        rate_mbr = reg.rate_mbr,
        medallion = reg.medallion,
        atd_paid = reg.atd_paid,
        price_paid = reg.price_paid,
        pay_type = reg.atd_pay_type,
        price_calc = reg.price_calc,
        price_due = reg.price_due,
        paypal_donation = reg.paypal_donation,
        paypal_donation_amount = reg.paypal_donation_amount,
        prereg_status = reg.prereg_status,
        early_on =reg.early_on,
        mbr_num = reg.mbr_num,
        mbr_num_exp = datetime.strptime(reg.mbr_num_exp, '%Y-%m-%d') if reg.mbr_num_exp is not None else None,
        onsite_contact_name = reg.onsite_contact_name,
        onsite_contact_sca_name = reg.onsite_contact_sca_name,
        onsite_contact_kingdom = reg.onsite_contact_kingdom,
        onsite_contact_group = reg.onsite_contact_group,
        offsite_contact_name = reg.offsite_contact_name,
        offsite_contact_phone = reg.offsite_contact_phone,
        notes = reg.notes
    )

    if reg.rate_date != None:
        try:
            form.rate_date.data = datetime.strptime(reg.rate_date, '%Y-%m-%d %H:%M:%S')
        except:
            form.rate_date.data = datetime.strptime(reg.rate_date, '%Y-%m-%d')

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

            if medallion_check is not None and int(regid) != int(medallion_check.regid):
                flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.regid) )
                dup_url = '<a href=' + url_for('troll.reg', regid=str(medallion_check.regid)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
                flash(Markup(dup_url))
            else:
                if request.form.get('medallion'):
                    reg.medallion = int(request.form.get('medallion'))
                else: reg.medallion = None

                reg.rate_mbr = request.form.get('rate_mbr')
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

            if medallion_check is not None and int(regid) != int(medallion_check.regid):
                flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " + str(medallion_check.regid) )
                dup_url = '<a href=' + url_for('troll.reg', regid=str(medallion_check.regid)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
                flash(Markup(dup_url))

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
                reg.rate_date = datetime.strptime(request.form.get('rate_date'), '%Y-%m-%d') if (request.form.get('rate_date') != '' and request.form.get('rate_date')) else None
                reg.rate_age = request.form.get('rate_age')
                reg.rate_mbr = request.form.get('rate_mbr')
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
                reg.prereg_status = request.form.get('prereg_status')
                reg.early_on = bool(request.form.get('early_on'))
                if request.form.get('mbr_num'):
                    reg.mbr_num = int(request.form.get('mbr_num'))
                else: reg.mbr_num = None
                if request.form.get('mbr_num_exp'):
                    reg.mbr_num_exp = request.form.get('mbr_num_exp')
                reg.onsite_contact_name = request.form.get('onsite_contact_name')
                reg.onsite_contact_sca_name = request.form.get('onsite_contact_sca_name')
                reg.onsite_contact_kingdom = request.form.get('onsite_contact_kingdom')
                reg.onsite_contact_group = request.form.get('onsite_contact_group')
                reg.offsite_contact_name = request.form.get('offsite_contact_name')
                reg.offsite_contact_phone = request.form.get('offsite_contact_phone') 

                reg.price_due = (reg.price_calc + reg.paypal_donation_amount) - (reg.price_paid + reg.atd_paid)
                if reg.price_due < 0:  #Account for people who showed up late.  No refund.
                    reg.price_due = 0

                db.session.commit()

                log_reg_action(reg, 'EDIT')

                return redirect(url_for('troll.reg',regid=regid))

    return render_template('editreg.html', regid=reg.regid, reg=reg, form=form)