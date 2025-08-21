from app.invoices import bp

from app.forms import *
from app.models import *
from app.utils.db_utils import *
from app.utils.email_utils import *
from app.utils.security_utils import *
from app.utils.paypal_api import *
from flask_security import roles_accepted
from markupsafe import Markup

from sqlalchemy import and_, or_

from flask import Flask, render_template, request, redirect, url_for, flash

from flask_login import login_required

@bp.route('/unsent', methods=('GET', 'POST'))
@login_required
@permission_required('invoice_view')
def unsent():
    all_regs = Registrations.query.filter(and_(Registrations.invoices == None, Registrations.prereg == True, Registrations.duplicate == False, Registrations.balance > 0)).order_by(Registrations.invoice_email).all()
    all_merchants = Merchant.query.filter(and_(Merchant.invoice_number == None, Merchant.status == "APPROVED")).all()
    all_earlyons = EarlyOnRequest.query.filter(and_(EarlyOnRequest.invoice_number == None, EarlyOnRequest.rider_balance > 0, EarlyOnRequest.dept_approval_status == 'APPROVED', EarlyOnRequest.autocrat_approval_status == 'APPROVED')).all()

    reg_invoices = {}
    for reg in all_regs:
        if reg.invoice_email not in reg_invoices:
            reg_invoices[reg.invoice_email] = {'invoice_type':'REGISTRATION','invoice_email':reg.invoice_email,'invoice_number':[inv.invoice_number for inv in reg.invoices], 'invoice_status':'UNSENT', 'invoice_date':None, 'registrations':[]}
        reg_invoices[reg.invoice_email]['registrations'].append(reg.id)
    
    merchant_invoices = {}
    for merchant in all_merchants:
        if merchant.email not in merchant_invoices:
            merchant_invoices[merchant.email] = {'invoice_type':'MERCHANT','invoice_email':merchant.email,'invoice_number':merchant.invoice_number, 'invoice_status':'UNSENT', 'invoice_date':None, 'registrations':[]}
        merchant_invoices[merchant.email]['registrations'].append(merchant.id)

    earlyon_invoices = {}
    for earlyon in all_earlyons:
        if earlyon.registration.invoice_email not in earlyon_invoices:
            earlyon_invoices[earlyon.registration.invoice_email] = {'invoice_type':'EARLYON','invoice_email':earlyon.registration.invoice_email,'invoice_number':earlyon.invoice_number, 'invoice_status':'UNSENT', 'invoice_date':None, 'registrations':[]}
        earlyon_invoices[earlyon.registration.invoice_email]['registrations'].append(earlyon.id)
    return render_template('unsent_list.html', reg_invoices=reg_invoices, merchant_invoices=merchant_invoices, earlyon_invoices=earlyon_invoices, counts=inv_prereg_unsent_counts())

@bp.route('/open', methods=('GET', 'POST'))
@login_required
@permission_required('invoice_view')
def open():
    all_inv = Invoice.query.filter(and_(Invoice.invoice_status == 'OPEN')).all()
    # all_regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.prereg == True, Registrations.invoice_status == 'OPEN')).order_by(Registrations.invoice_email).all()
    return render_template('open_list.html', invoices=all_inv, counts=inv_prereg_open_counts())

@bp.route('/paid', methods=('GET', 'POST'))
@login_required
@permission_required('invoice_view')
def paid():
    all_inv = Invoice.query.filter(Invoice.invoice_status == 'PAID').all()
    # all_regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.prereg == True, Registrations.invoice_status == 'OPEN')).order_by(Registrations.invoice_email).all()
    return render_template('paid_list.html', invoices=all_inv, counts=inv_prereg_paid_counts())

@bp.route('/canceled', methods=('GET', 'POST'))
@login_required
@permission_required('invoice_view')
def canceled():
    all_inv = Invoice.query.filter(Invoice.invoice_status == 'CANCELED').all()
    # invoices = {}
    # for reg in all_inv:
    #     if reg.invoice_email not in invoices:
    #         invoices[reg.invoice_email] = {'invoice_email':reg.invoice_email,'invoice_number':reg.invoice_number, 'invoice_status':reg.invoice_status, 'invoice_date':reg.invoice_date, 'registrations':[]}
    #     invoices[reg.invoice_email]['registrations'].append(reg.id)
    return render_template('invoice_list.html', invoices=all_inv, back='canceled', counts=inv_prereg_canceled_counts())

@bp.route('/all', methods=('GET', 'POST'))
@login_required
@permission_required('invoice_view')
def all():

    all_inv = Invoice.query.all()

    # invoices = {}
    # for reg in all_inv:
    #     if reg.invoice_email not in invoices:
    #         invoices[reg.invoice_email] = {'invoice_email':reg.invoice_email,'invoice_number':reg.invoice_number, 'invoice_status':reg.invoice_status, 'invoice_date':reg.invoice_date, 'invoice_total':0, 'registrations':[]}
    #     invoices[reg.invoice_email]['invoice_total'] += reg.total_due

    #     invoices[reg.invoice_email]['registrations'].append(reg.id)
    now = datetime.now(pytz.timezone('America/Chicago'))
    return render_template('invoice_list.html', invoices=all_inv, back='all', now=now, counts=inv_prereg_all_counts())

@bp.route('/update', methods=('GET', 'POST'))
@login_required
@permission_required('invoice_edit')
def update():
    invnumber = request.args.get('invnumber')
    inv = get_inv(invnumber)
    if inv.invoice_type == 'REGISTRATION':
        regs = []
        for r in inv.regs:
            if r.duplicate == False:
                regs.append(r)
    elif inv.invoice_type == 'MERCHANT':
        regs = inv.merchants
    elif inv.invoice_type == 'EARLYON':
        regs = inv.earlyonrequests
    pays = inv.payments

    form = UpdateInvoiceForm()
    form.invoice_amount.data = inv.invoice_total
    form.registration_amount.data = inv.registration_total
    form.invoice_number.data  = inv.invoice_number
    form.invoice_status.data  = inv.invoice_status
    form.paypal_donation.data  = inv.donation_total
    form.invoice_date.data  = inv.invoice_date
    form.notes.data  = inv.notes
    form.invoice_email.data = inv.invoice_email
    form.notes.data = inv.notes
    
    if request.method == 'POST':
        invoice_number = request.form.get('invoice_number')
        invoice_date = request.form.get('invoice_date')
        invoice_email = request.form.get('invoice_email')
        payment_date = request.form.get('payment_date')
        payment_amount = int(request.form.get('payment_amount'))
        payment_type = request.form.get('payment_type')
        check_num = request.form.get('check_num')
        notes = request.form.get('notes')

        if invoice_number is not None:
            inv.invoice_number = invoice_number
            inv.invoice_email = invoice_email
            inv.invoice_date = invoice_date
            inv.invoice_status = request.form.get('invoice_status')
            inv.registration_total = request.form.get('registration_total')
            inv.nmr_total = request.form.get('nmr_total')
            inv.donation_total = request.form.get('donation_total')
            inv.notes = notes

        if payment_amount is not None:
            pays[0].type = payment_type
            pays[0].check_num = check_num if check_num != '' else None
            pays[0].payment_date = payment_date
            pays[0].amount = payment_amount

            inv.balance = inv.balance - pays[0].amount

            for reg in regs:      
                reg.invoice_number = invoice_number

        db.session.commit()

        # log_reg_action(reg, 'INVOICE UPDATED')

    return render_template('update_invoice.html', form=form, regs=regs, inv=inv)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@permission_required('invoice_edit')
def createinvoice():
    regids = request.args.get('regids')
    type = request.args.get('type')
    form = SendInvoiceForm()
    if type == 'REGISTRATION':
        regs = get_regs(regids)
        paypal_donation = 0
        registration_price = 0
        nmr_price = 0
        total_due = 0
        for reg in regs:
            if reg.duplicate == False:
                paypal_donation += reg.paypal_donation
                registration_price += reg.registration_price
                nmr_price += reg.nmr_price
                total_due += reg.total_due
        form.paypal_donation.data = paypal_donation
        form.registration_amount.data = registration_price + nmr_price
        form.nmr_amount.data = nmr_price
        form.invoice_amount.data = total_due
        form.invoice_date.data = datetime.now(pytz.timezone('America/Chicago'))
        form.invoice_email.data = reg.invoice_email
    elif type == 'MERCHANT':
        merchants = get_merchants(regids)
        processing_fee = 0
        space_fee = 0
        for merchant in merchants:
            processing_fee += merchant.processing_fee
            space_fee += merchant.space_fee
        form.space_fee.data = space_fee
        form.processing_fee.data = processing_fee
        form.merchant_fee.data = space_fee + processing_fee
        form.invoice_date.data = datetime.now(pytz.timezone('America/Chicago'))
        form.invoice_email.data = merchant.email
        regs = merchants
    elif type == 'EARLYON':
        earlyons = get_earlyon(regids)
        rider_fee = 0
        for earlyon in earlyons:
            rider_fee += earlyon.rider_cost
        form.rider_fee.data = rider_fee
        form.invoice_date.data = datetime.now(pytz.timezone('America/Chicago'))
        form.invoice_email.data = earlyon.registration.invoice_email
        regs = earlyons
    
    if request.method == 'POST' and form.validate_on_submit():
        # invoice_number = request.form.get('invoice_number')
        invoice_date = request.form.get('invoice_date')
        invoice_email = request.form.get('invoice_email')
        notes = request.form.get('notes')

        # dup_inv = Invoice.query.filter(Invoice.invoice_number==invoice_number).first()

        # if dup_inv is not None:
        #     dup_url = '<a href=' + url_for('invoices.update', invnumber=str(dup_inv.invoice_number)) + ' target="_blank" rel="noopener noreferrer">Duplicate</a>'
        #     flash("Invoice Number " + str(dup_inv.invoice_number) +" already exists. " + Markup(dup_url),'error')
        #     return render_template('create_invoice.html', form=form, regs=regs, type=type)
        
        if type == 'REGISTRATION':
            # Create a new invoice for the registrations
            paypal_invoice = create_invoice(regs, invoice_email)

            inv = Invoice(
                invoice_type = 'REGISTRATION',
                invoice_number = paypal_invoice['detail']['invoice_number'],
                invoice_id = paypal_invoice['id'],
                invoice_email = invoice_email,
                invoice_date = invoice_date,
                invoice_status = 'OPEN',
                registration_total = registration_price,
                nmr_total = nmr_price,
                donation_total = paypal_donation,
                balance = total_due,
                notes = notes,
                # event_id = regs[0].event_id,
            )

            send_invoice(paypal_invoice['id'])

            for reg in regs:
                if reg.duplicate == False:      
                    reg.invoices.append(inv)

            db.session.add(inv)
            db.session.commit()
        
        elif type == 'MERCHANT':
            # Create a new invoice for the merchant
            paypal_invoice = create_invoice(merchants, invoice_email)

            inv = Invoice(
                invoice_type = 'MERCHANT',
                invoice_number = paypal_invoice['detail']['invoice_number'],
                invoice_id = paypal_invoice['id'],
                invoice_email = invoice_email,
                invoice_date = invoice_date,
                invoice_status = 'OPEN',
                space_fee = space_fee,
                processing_fee = processing_fee,
                balance = space_fee + processing_fee,
                notes = notes,
                # event_id = regs[0].event_id,
            )

            send_invoice(paypal_invoice['id'])

            for merchant in merchants:      
                merchant.invoice_number = inv.invoice_number
            
            db.session.add(inv)
            db.session.commit()

        elif type == 'EARLYON':
            # Create a new invoice for the earlyons
            paypal_invoice = create_invoice(earlyons, invoice_email)

            inv = Invoice(
                invoice_type = 'EARLYON',
                invoice_number = paypal_invoice['detail']['invoice_number'],
                invoice_id = paypal_invoice['id'],
                invoice_email = invoice_email,
                invoice_date = invoice_date,
                invoice_status = 'OPEN',
                rider_fee = rider_fee,
                balance = rider_fee,
                notes = notes,
            )

            send_invoice(paypal_invoice['id'])

            for earlyon in earlyons:
                earlyon.invoice_number = inv.invoice_number

            db.session.add(inv)
            db.session.commit()

        return redirect(url_for('invoices.unsent'))

    return render_template('create_invoice.html', form=form, regs=regs, type=type)

@bp.route('/payment', methods=('GET', 'POST'))
@login_required
@permission_required('invoice_edit')
def createpayment():
    invnumber = request.args.get('invnumber')
    inv = get_inv(invnumber)
    if inv.invoice_type == 'REGISTRATION':
        regs = []
        for r in inv.regs:
            if r.duplicate == False:
                regs.append(r)
    elif inv.invoice_type == 'MERCHANT':
        regs = inv.merchants
    elif inv.invoice_type == 'EARLYON':
        regs = inv.earlyonrequests

    form = PayInvoiceForm()
    form.invoice_amount.data = inv.balance
    form.registration_amount.data = inv.registration_total
    form.invoice_number.data  = inv.invoice_number
    form.invoice_status.data  = inv.invoice_status
    form.paypal_donation.data  = inv.donation_total
    form.invoice_date.data  = inv.invoice_date
    form.notes.data  = inv.notes
    form.invoice_email.data = inv.invoice_email
    form.processing_fee.data = inv.processing_fee
    form.space_fee.data = inv.space_fee
    form.rider_fee.data = inv.rider_fee
    
    if request.method == 'POST' and form.validate_on_submit():
        # payment_date = DateField('Payment Date')
        # payment_amount = IntegerField('Payment Amount')
        # payment_type = SelectField('Payment Type',choices=[('PAYPAL','PAYPAL'),('CHECK','CHECK')])
        # check_num = IntegerField('Check Number')

        invoice_number = request.form.get('invoice_number')
        payment_date = request.form.get('payment_date')
        payment_amount = float(request.form.get('payment_amount'))
        payment_type = request.form.get('payment_type')
        check_num = request.form.get('check_num')
        notes = request.form.get('notes')
        
        if payment_amount is not None and inv.invoice_type == 'REGISTRATION':
            payment_balance = payment_amount
            for reg in regs:
                if payment_balance > 0 and reg.balance > 0:
                    pay = Payment(
                        type = payment_type,
                        check_num = check_num if check_num != '' else None,
                        payment_date = payment_date,
                        reg_id = reg.id,
                        reg = reg,
                        invoice_number = invoice_number,
                    )
                    pay.calculate_payment_amounts(payment_balance)
                    db.session.add(pay)
                    payment_balance -= (reg.registration_balance + reg.nmr_balance + reg.paypal_donation_balance)
                    if notes is not None and reg.notes is not None:
                        reg.notes += "\nInvocie Notes: " + notes
                    elif notes is not None and reg.notes is None:
                        reg.notes = "\nInvocie Notes: " + notes
                    reg.recalculate_balance()
                    db.session.commit()

            inv.balance = float(inv.balance) - float(payment_amount)
            if inv.balance <= 0:
                inv.invoice_status = 'PAID'
                for r in inv.regs:
                    if r.duplicate == True:
                        r.invoice_number = None
                    else:
                        send_fastpass_email(r.email, r)
            inv.notes += notes

            db.session.commit()

        elif payment_amount is not None and inv.invoice_type == 'MERCHANT':
            payment_balance = payment_amount
            for reg in regs:
                if payment_balance > 0:
                    pay = Payment(
                        type = payment_type,
                        check_num = check_num if check_num != '' else None,
                        payment_date = payment_date,
                        merchant_id = reg.id,
                        merchant = reg,
                        invoice_number  = invoice_number,
                    )

                    pay.calculate_payment_amounts(payment_balance)
                    db.session.add(pay)
                    payment_balance -= (float(reg.space_fee_balance) + reg.processing_fee_balance + float(reg.electricity_balance))
                    reg.notes = notes
                    reg.recalculate_balance()
                    db.session.commit()

            inv.balance = float(inv.balance) - float(payment_amount)
            if inv.balance <= 0:
                inv.invoice_status = 'PAID'
            inv.notes = notes

            db.session.commit()

        elif payment_amount is not None and inv.invoice_type == 'EARLYON':
            payment_balance = payment_amount
            for reg in regs:
                if payment_balance > 0:
                    pay = Payment(
                        type = payment_type,
                        check_num = check_num if check_num != '' else None,
                        payment_date = payment_date,
                        earlyonrequest_id = reg.id,
                        earlyonrequest = reg,
                        invoice_number  = invoice_number,
                    )
                    pay.calculate_payment_amounts(payment_balance)
                    db.session.add(pay)
                    payment_balance -= reg.rider_balance
                    reg.notes = notes
                    reg.recalculate_balance()
                    db.session.commit()

            inv.balance = float(inv.balance) - float(payment_amount)
            if inv.balance <= 0:
                inv.invoice_status = 'PAID'
                #TODO: CREATE EARLY ON EMAIL
            inv.notes = notes

            if reg.rider_balance <= 0 and reg.dept_approval_status == 'APPROVED' and reg.autocrat_approval_status == 'APPROVED':
                reg.registration.early_on_approved = True
                for rider in reg.earlyonriders:
                    rider.reg.early_on_approved = True

            db.session.commit()

        return redirect(url_for('invoices.open'))

    return render_template('create_payment.html', form=form, regs=regs, inv=inv)


# @bp.route('/payment', methods=('GET', 'POST'))
# @login_required
# @roles_accepted('Admin','Invoices','Department Head')
# def payment():
#     regids = request.args.get('regids')
#     regs = get_regs(regids)
#     paypal_donation = 0
#     registration_price = 0
#     nmr_price = 0
#     total_due = 0
#     for reg in regs:
#         paypal_donation += reg.paypal_donation
#         registration_price += reg.registration_price
#         nmr_price += reg.nmr_price
#         total_due += reg.total_due
#     form = PayInvoiceForm()
#     form.paypal_donation.data = paypal_donation
#     form.invoice_number.data = reg.invoice_number
#     form.invoice_status.data = reg.invoice_status
#     form.invoice_amount.data = total_due