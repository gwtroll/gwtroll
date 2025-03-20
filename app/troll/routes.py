from flask import render_template
from app.troll import bp

from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, url_for, flash, redirect
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted
import json
from markupsafe import Markup

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

@bp.route('/checkin', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin','Troll Shift Lead','Troll User','Department Head')
def checkin():
    regid = request.args['regid']
    reg = get_reg(regid)

    form = CheckinForm(kingdom = reg.kingdom, rate_mbr = reg.rate_mbr, medallion = reg.medallion, rate_age = reg.rate_age, lodging = reg.lodging, notes=reg.notes, mbr_num=reg.mbr_num)
    if reg.mbr_num_exp is not None:
        form.mbr_num_exp.data = datetime.strptime(reg.mbr_num_exp, '%Y-%m-%d')
    price_paid = reg.price_paid
    price_calc = reg.price_calc
    kingdom = reg.kingdom
    rate_mbr = reg.rate_mbr
    rate_age = reg.rate_age

    #if form.validate_on_submit():
        #print(form)
    #Calculate Total Price

    #today = int(datetime.today().date().strftime('%-d'))  #Get today's day to calculate pricing

    #Check for medallion number    

    if request.method == 'POST':
        if form.rate_mbr.data == 'Member':
            if request.form.get('mbr_num') is None:
                flash('Membership Number is Required if Member.')
                return render_template('checkin.html', reg=reg, form=form) 
            elif request.form.get('mbr_num_exp') is None:
                flash('Membership Expiration Date is Required if Member.')
                return render_template('checkin.html', reg=reg, form=form)
            elif datetime.strptime(request.form.get('mbr_num_exp'),'%Y-%m-%d').date() < datetime.now().date():
                flash('Membership Expiration Date {} is not current.'.format(request.form.get('mbr_num_exp')))
                return render_template('checkin.html', reg=reg, form=form)
        medallion = form.medallion.data
        kingdom = form.kingdom.data
        rate_mbr = form.rate_mbr.data
        lodging = form.lodging.data
        minor_waiver = form.minor_waiver.data
        
        if form.minor_waiver.data == '-':
            flash('You must select a Minor Waiver Validation')
            return render_template('checkin.html', reg=reg, form=form)

        if request.form.get('medallion') != '' and request.form.get('medallion') != None:
            medallion_check = Registrations.query.filter_by(medallion=form.medallion.data).first()
        else:
            medallion_check = None

        if medallion_check is not None and int(regid) != int(medallion_check.regid):
            duplicate_name = medallion_check.fname + " " + medallion_check.lname
            dup_url = '<a href=' + url_for('troll.reg', regid=str(medallion_check.regid)) + f' target="_blank" rel="noopener noreferrer">{duplicate_name}</a>'
            flash("Medallion # " + str(medallion_check.medallion) + " already assigned to " +  Markup(dup_url))
        else:
            #Account for PreReg Non-Member and Checkin Member (No NMR Refund - View as Donation)
            if reg.rate_mbr != 'Member' and rate_mbr == 'Member' and reg.prereg_status == 'SUCCEEDED' and reg.rate_age.__contains__('18+'):
                nmr_donation = 10
            else:
                nmr_donation = 0
            reg.medallion = medallion
            reg.rate_mbr = rate_mbr
            reg.rate_age = rate_age
            reg.kingdom = kingdom
            # UNCOMMENT ONCE DB UPDATED - MINOR WAIVER STATUS
            reg.minor_waiver = minor_waiver
            reg.lodging = lodging
            reg.checkin = datetime.today()
            reg.price_calc = calculate_price_calc(reg)
            reg.nmr_donation = nmr_donation
            reg.notes = form.notes.data

            #Calculate Price Due
            if price_paid > price_calc + reg.paypal_donation_amount:  #Account for people who showed up late.  No refund.
                reg.price_due = 0
            else:
                reg.price_due = (reg.price_calc + reg.paypal_donation_amount) - (reg.price_paid + reg.atd_paid)
                print("Calculating price:", reg.price_calc) 

            db.session.commit()

            log_reg_action(reg, 'CHECKIN')

            return redirect(url_for('troll.reg', regid=regid))

    return render_template('checkin.html', reg=reg, form=form)

@bp.route('/waiver', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "Troll Shift Lead", "Troll User",'Department Head')
def waiver():
    form = WaiverForm()
    regid = request.args['regid']
    reg = get_reg(regid)
    form.paypal_donation.data = reg.paypal_donation
    if request.method == 'POST':

        if reg.paypal_donation == False and bool(request.form.get('paypal_donation')) == True:
            reg.paypal_donation_amount = 3
        elif reg.paypal_donation == True and bool(request.form.get('paypal_donation')) == False:            
            reg.paypal_donation_amount = 0
        reg.paypal_donation = bool(request.form.get('paypal_donation'))
        reg.price_due = (reg.price_calc + reg.paypal_donation_amount) - reg.price_paid
        reg.signature = form.signature.data
        
        db.session.commit()

        log_reg_action(reg, 'WAIVER')

        return redirect(url_for('troll.reg', regid=regid))

    return render_template('waiver.html', form=form, reg=reg)

@bp.route('/payment', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "Troll User", "Troll Shift Lead",'Department Head')
def payment():
    form = EditForm()
    regid = request.args['regid']
    reg = get_reg(regid)
    form.fname.data = reg.fname
    form.lname.data = reg.lname
    form.scaname.data = reg.scaname
    form.invoice_email.data = reg.invoice_email
    form.price_calc.data = reg.price_calc
    form.price_due.data = reg.price_due
    form.pay_type.data = reg.atd_pay_type
    if request.method == 'POST':

        if request.form.get('pay_type') == '':
            flash('Must select a Payment Type')
            return redirect(url_for('troll.payment', regid=regid, form=form))

        # reg.atd_paid = form.atd_paid.data
        # if reg.price_paid + reg.atd_paid > reg.price_calc:  #Account for people who showed up late.  No refund.
        #     reg.price_due = 0
        # else:
        #     reg.price_due = reg.price_calc - (reg.price_paid + reg.atd_paid)

        reg.atd_pay_type = request.form.get('pay_type')
        reg.atd_paid += reg.price_due
        reg.price_due = 0
        db.session.commit()

        log_reg_action(reg, 'PAYMENT')

        return redirect(url_for('troll.reg', regid=regid))

    return render_template('payment.html', form=form)