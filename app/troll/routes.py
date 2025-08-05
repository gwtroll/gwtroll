from app.troll import bp

from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, url_for, flash, redirect, jsonify
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from app.utils.security_utils import *
from flask_security import roles_accepted
import json
from markupsafe import Markup

import base64
import numpy as np

@bp.route('/<int:regid>', methods=('GET', 'POST'))
@login_required
@permission_required('troll')
def reg(regid):
    reg = get_reg(regid)
    atd_payments = []
    for pay in reg.payments:
        if pay.type.upper() != 'PAYPAL' and pay.type.upper() != 'CHECK':
            atd_payments.append(pay)
    return render_template('reg.html', reg=reg, atd_payments=atd_payments)
    
@bp.route('/fastpass')
@login_required
@permission_required('troll')
def fastpass():
        return render_template('fastpass.html')

@bp.route('/<int:regid>/checkin', methods=['GET', 'POST'])
@login_required
@permission_required('troll')
def checkin(regid):
    # regid = request.args['regid']
    reg = get_reg(regid)

    form = CheckinForm(
        kingdom = reg.kingdom_id, 
        mbr = 'Member' if reg.mbr else 'Non-Member', 
        mbr_num = reg.mbr_num,
        mbr_num_exp = reg.mbr_num_exp,
        medallion = reg.medallion, 
        age = reg.age, 
        lodging = reg.lodging_id, 
        notes=reg.notes, 
    )
    form.lodging.choices = get_lodging_choices()
    form.kingdom.choices = get_kingdom_choices()
    if reg.mbr_num_exp is not None:
        form.mbr_num_exp.data = reg.mbr_num_exp

    #if form.validate_on_submit():
        #print(form)
    #Calculate Total Price

    #today = int(datetime.today().date().strftime('%-d'))  #Get today's day to calculate pricing

    #Check for medallion number    

    if request.method == 'POST' and form.validate_on_submit():
        if form.mbr.data == 'Member':
            if request.form.get('mbr_num') is None:
                flash('Membership Number is Required if Member.','error')
                return render_template('checkin.html', reg=reg, form=form) 
            elif request.form.get('mbr_num_exp') is None:
                flash('Membership Expiration Date is Required if Member.','error')
                return render_template('checkin.html', reg=reg, form=form)
            elif datetime.strptime(request.form.get('mbr_num_exp'),'%Y-%m-%d').date() < datetime.now(pytz.timezone('America/Chicago')).date():
                flash('Membership Expiration Date {} is not current.'.format(request.form.get('mbr_num_exp')),'error')
                return render_template('checkin.html', reg=reg, form=form)
        medallion = form.medallion.data
        kingdom = form.kingdom.data
        mbr = form.mbr.data
        mbr_num = form.mbr_num.data
        mbr_num_exp = form.mbr_num_exp.data
        age = form.age.data
        lodging = form.lodging.data
        minor_waiver = form.minor_waiver.data
        
        if form.minor_waiver.data == '-':
            flash('You must select a Minor Waiver Validation','error')
            return render_template('checkin.html', reg=reg, form=form)

        if request.form.get('medallion') != '' and request.form.get('medallion') != None:
            medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()
        else:
            medallion_check = None

        if medallion_check is not None and int(regid) != int(medallion_check.id):
            duplicate_name = medallion_check.fname + " " + medallion_check.lname
            dup_url = '<a href=' + url_for('troll.reg', regid=str(medallion_check.id)) + f' target="_blank" rel="noopener noreferrer">{duplicate_name}</a>'
            flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " +  Markup(dup_url),'error')
        else:
            #Account for PreReg Non-Member and Checkin Member (No NMR Refund - View as Donation)
            if reg.mbr != True and mbr == 'Member' and reg.prereg == True and reg.age.__contains__('18+'):
                reg.nmr_donation = 10
            else:
                reg.nmr_donation = 0

            if reg.mbr == True and mbr != 'Member' and reg.age.__contains__('18+'):
                reg.nmr_price = 10
                reg.nmr_balance = 10

            reg.medallion = medallion
            reg.mbr = True if mbr == 'Member' else False
            reg.mbr_num = mbr_num
            reg.mbr_num_exp = mbr_num_exp
            reg.age = age
            reg.kingdom_id = kingdom
            reg.minor_waiver = minor_waiver
            reg.lodging_id = lodging
            reg.checkin = datetime.now(pytz.timezone('America/Chicago'))
            reg.actual_arrival_date = datetime.now(pytz.timezone('America/Chicago')).date()

            reg.notes = form.notes.data

            #Calculate Price Due
            if reg.age == '18+':
                if reg.prereg == True:
                    registration_price = get_prereg_pricesheet_day(reg.actual_arrival_date)
                else:
                    registration_price = get_atd_pricesheet_day(reg.actual_arrival_date)
                if reg.registration_price < registration_price:
                    # reg.registration_balance = registration_price - reg.registration_price
                    reg.registration_price = registration_price
            
            # reg.balance = reg.registration_balance + reg.nmr_balance + reg.paypal_donation_balance
            reg.recalculate_balance()

            db.session.commit()

            # log_reg_action(reg, 'CHECKIN')

            if reg.balance > 0:
                return redirect(url_for('troll.payment', regid=regid))
            else:
                flash(f"{reg.fname} {reg.lname} successfully checked in!")
                return redirect(url_for('index', regid=regid))

    return render_template('checkin.html', reg=reg, form=form)

@bp.route('/<int:regid>/waiver', methods=['GET', 'POST'])
@login_required
@permission_required('troll')
def waiver(regid):
    event = EventVariables.query.first()
    form = WaiverForm()
    # regid = request.args['regid']
    reg = get_reg(regid)
    
    if request.method == 'POST' and form.validate_on_submit():
        if bool(request.form.get('paypal_donation')) == True:
            reg.paypal_donation = int(request.form.get('paypal_donation_amount'))
            reg.paypal_donation_balance = int(request.form.get('paypal_donation_amount'))

        reg.signature = form.signature.data

        reg.recalculate_balance()
        
        db.session.commit()

        # log_reg_action(reg, 'WAIVER')

        return redirect(url_for('troll.checkin', regid=regid))

    return render_template('waiver.html', form=form, reg=reg, event=event)

@bp.route('/<int:regid>/updatedonation', methods=['POST', ''])
@login_required
@permission_required('troll')
def updatedonation(regid):
    reg = get_reg(regid)
    if bool(request.form.get('paypal_donation')) == False:
        reg.paypal_donation = 0
        reg.paypal_donation_balance = 0
    elif bool(request.form.get('paypal_donation')) == True:
        reg.paypal_donation = int(request.form.get('paypal_donation_amount'))
        reg.paypal_donation_balance = int(request.form.get('paypal_donation_amount'))
    reg.recalculate_balance()
    db.session.commit()
    return redirect(url_for('troll.payment', regid=regid))

@bp.route('/<int:regid>/payment', methods=['GET', 'POST'])
@login_required
@permission_required('troll')
def payment(regid):
    form = PayRegistrationForm()
    paypal_form = UpdatePayPalDonationForm()
    # regid = request.args['regid']
    reg = get_reg(regid)

    paypal_form.paypal_donation.data = True if reg.paypal_donation > 0 else False
    paypal_form.paypal_donation_amount.data = reg.paypal_donation

    form.total_due.data = reg.balance

    if request.method == 'POST':

        if request.form.get('payment_type') == '':
            flash('Must select a Payment Type','error')
            return redirect(url_for('troll.payment', regid=regid, form=form))

        # reg.atd_paid = form.atd_paid.data
        # if reg.price_paid + reg.atd_paid > reg.price_calc:  #Account for people who showed up late.  No refund.
        #     reg.price_due = 0
        # else:
        #     reg.price_due = reg.price_calc - (reg.price_paid + reg.atd_paid)
        
        pay = Payment(
            type = request.form.get('payment_type'),
            payment_date = datetime.now(pytz.timezone('America/Chicago')).date(),
            registration_amount = reg.registration_balance,
            nmr_amount = reg.nmr_balance,
            paypal_donation_amount = reg.paypal_donation_balance,
            amount = reg.balance,
            reg_id = reg.id,
            # event_id = reg.event_id
        )

        if pay.amount > 0:
            db.session.add(pay)
            db.session.commit()

            reg.recalculate_balance()
            db.session.commit()

        # log_reg_action(reg, 'PAYMENT')

        return redirect(url_for('troll.reg', regid=regid))

    return render_template('payment.html', form=form, reg=reg, paypal_form=paypal_form)