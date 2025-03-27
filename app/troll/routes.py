from app.troll import bp

from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, url_for, flash, redirect, jsonify
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted
import json
from markupsafe import Markup

import base64
import numpy as np
import cv2
from pyzbar import pyzbar

@bp.route('/<int:regid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Troll Shift Lead','Troll User','Cashier','Department Head')
def reg(regid):
    reg = get_reg(regid)
    if request.form.get("action") == 'Edit':
    #if request.method == 'POST' and request.path == '/editreg':
        return redirect(url_for('registration.editreg', regid=regid))
    elif request.method == 'POST' and request.form.get("action") == 'waiver':
        return redirect(url_for('troll.waiver', regid=regid))
    elif request.method == 'POST' and request.form.get("action") == 'payment':
        return redirect(url_for('troll.payment', regid=regid))
    elif request.method == 'POST'and request.form.get("action") == 'checkin':
        return redirect(url_for('troll.checkin', regid=regid))
    else:
        return render_template('reg.html', reg=reg)
    
@bp.route('/fastpass')
def fastpass():
        return render_template('fastpass.html')


@bp.route('/checkin', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin','Troll Shift Lead','Troll User','Department Head')
def checkin():
    regid = request.args['regid']
    reg = get_reg(regid)

    form = CheckinForm(kingdom = reg.kingdom, mbr = reg.mbr, medallion = reg.medallion, age = reg.age, lodging = reg.lodging, notes=reg.notes, mbr_num=reg.mbr_num)
    if reg.mbr_num_exp is not None:
        form.mbr_num_exp.data = datetime.strptime(reg.mbr_num_exp, '%Y-%m-%d')

    kingdom = reg.kingdom
    mbr = reg.mbr
    age = reg.age

    #if form.validate_on_submit():
        #print(form)
    #Calculate Total Price

    #today = int(datetime.today().date().strftime('%-d'))  #Get today's day to calculate pricing

    #Check for medallion number    

    if request.method == 'POST':
        if form.mbr.data == 'Member':
            if request.form.get('mbr_num') is None:
                flash('Membership Number is Required if Member.','error')
                return render_template('checkin.html', reg=reg, form=form) 
            elif request.form.get('mbr_num_exp') is None:
                flash('Membership Expiration Date is Required if Member.','error')
                return render_template('checkin.html', reg=reg, form=form)
            elif datetime.strptime(request.form.get('mbr_num_exp'),'%Y-%m-%d').date() < datetime.now().date():
                flash('Membership Expiration Date {} is not current.'.format(request.form.get('mbr_num_exp')),'error')
                return render_template('checkin.html', reg=reg, form=form)
        medallion = form.medallion.data
        kingdom = form.kingdom.data
        mbr = form.mbr.data
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
                reg.nmr_price = 0
            else:
                reg.nmr_donation = 0
            reg.medallion = medallion
            reg.mbr = True if mbr == 'Member' else False
            reg.age = age
            reg.kingdom = kingdom
            # UNCOMMENT ONCE DB UPDATED - MINOR WAIVER STATUS
            reg.minor_waiver = minor_waiver
            reg.lodging = lodging
            reg.checkin = datetime.today()

            reg.notes = form.notes.data

            #Calculate Price Due
            # if price_paid > price_calc + reg.paypal_donation_amount:  #Account for people who showed up late.  No refund.
            #     reg.price_due = 0
            # else:
            #     reg.price_due = (reg.price_calc + reg.paypal_donation_amount) - (reg.price_paid + reg.atd_paid)
            #     print("Calculating price:", reg.price_calc) 

            db.session.commit()

            log_reg_action(reg, 'CHECKIN')

            if reg.balance > 0:
                return redirect(url_for('troll.payment', regid=regid))
            else:
                flash(f"{reg.fname} {reg.lname} successfully checked in!")
                return redirect(url_for('index', regid=regid))

    return render_template('checkin.html', reg=reg, form=form)

@bp.route('/waiver', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "Troll Shift Lead", "Troll User",'Department Head')
def waiver():
    form = WaiverForm()
    regid = request.args['regid']
    reg = get_reg(regid)
    form.paypal_donation.data = True if reg.paypal_donation > 0 else False
    if request.method == 'POST':
        if bool(request.form.get('paypal_donation')) == True:
            reg.paypal_donation = 3
        else:
            reg.paypal_donation = 0

        reg.signature = form.signature.data
        
        db.session.commit()

        log_reg_action(reg, 'WAIVER')

        return redirect(url_for('troll.checkin', regid=regid))

    return render_template('waiver.html', form=form, reg=reg)

@bp.route('/payment', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "Troll User", "Troll Shift Lead",'Department Head')
def payment():
    form = PayRegistrationForm()
    regid = request.args['regid']
    reg = get_reg(regid)

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
            payment_date = datetime.now().date(),
            amount = reg.balance
        )

        db.session.add(pay)
        db.session.commit()

        reg.payment_id = pay.id
        reg.balance = recalculate_reg_balance(reg)

        db.session.commit()

        log_reg_action(reg, 'PAYMENT')

        return redirect(url_for('troll.reg', regid=regid))

    return render_template('payment.html', form=form)