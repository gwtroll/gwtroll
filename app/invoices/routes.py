from app.invoices import bp

from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted

from sqlalchemy import and_, or_

from flask import Flask, render_template, request, redirect, url_for

from flask_login import login_required

@bp.route('/unsent', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def unsent():
    if current_user.event_id:
        all_regs = Registrations.query.filter(and_(Registrations.invoice_number == None, Registrations.prereg == True, Registrations.duplicate == False, Registrations.event_id == current_user.event_id)).order_by(Registrations.invoice_email).all()
        all_merchants = Merchant.query.filter(and_(Merchant.event_id == current_user.event_id, Merchant.invoice_number == None, Merchant.status == "APPROVED")).all()
    else:
        all_regs = Registrations.query.filter(and_(Registrations.invoice_number == None, Registrations.prereg == True, Registrations.duplicate == False)).order_by(Registrations.invoice_email).all()
        all_merchants = Merchant.query.filter(and_(Merchant.invoice_number == None, Merchant.status == "APPROVED")).all()

    # preregtotal = prereg_total()
    # invoicecount = unsent_count()
    # regcount = unsent_reg_count()
    reg_invoices = {}
    for reg in all_regs:
        if reg.invoice_email not in reg_invoices:
            reg_invoices[reg.invoice_email] = {'invoice_type':'REGISTRATION','invoice_email':reg.invoice_email,'invoice_number':reg.invoice_number, 'invoice_status':'UNSENT', 'invoice_date':None, 'registrations':[]}
        reg_invoices[reg.invoice_email]['registrations'].append(reg.id)
    
    merchant_invoices = {}
    for merchant in all_merchants:
        if merchant.email not in merchant_invoices:
            merchant_invoices[merchant.email] = {'invoice_type':'MERCHANT','invoice_email':merchant.email,'invoice_number':merchant.invoice_number, 'invoice_status':'UNSENT', 'invoice_date':None, 'registrations':[]}
        merchant_invoices[merchant.email]['registrations'].append(merchant.id)

    return render_template('unsent_list.html', reg_invoices=reg_invoices, merchant_invoices=merchant_invoices)

@bp.route('/open', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def open():
    if current_user.event_id:
        all_inv = Invoice.query.filter(and_(Invoice.invoice_status == 'OPEN', Invoice.event_id == current_user.event_id)).all()
    else:
        all_inv = Invoice.query.filter(and_(Invoice.invoice_status == 'OPEN', Invoice.event_id == current_user.event_id)).all()
    # all_regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.prereg == True, Registrations.invoice_status == 'OPEN')).order_by(Registrations.invoice_email).all()
    # preregtotal = prereg_total()
    # invoicecount = unsent_count()
    # regcount = unsent_reg_count()
    return render_template('open_list.html', invoices=all_inv)

@bp.route('/paid', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def paid():
    if current_user.event_id:
        all_inv = Invoice.query.filter(and_(Invoice.invoice_status == 'PAID', Invoice.event_id == current_user.event_id)).all()
    else:
        all_inv = Invoice.query.filter(Invoice.invoice_status == 'PAID').all()
    # all_regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.prereg == True, Registrations.invoice_status == 'OPEN')).order_by(Registrations.invoice_email).all()
    # preregtotal = prereg_total()
    # invoicecount = unsent_count()
    # regcount = unsent_reg_count()
    return render_template('paid_list.html', invoices=all_inv)

@bp.route('/canceled', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def canceled():
    if current_user.event_id:
        all_inv = Invoice.query.filter(and_(Invoice.invoice_status == 'CANCELED', Invoice.event_id == current_user.event_id)).all()
    else:
        all_inv = Invoice.query.filter(Invoice.invoice_status == 'CANCELED').all()
    # preregtotal = prereg_total()
    # invoicecount = unsent_count()
    # regcount = unsent_reg_count()
    # invoices = {}
    # for reg in all_inv:
    #     if reg.invoice_email not in invoices:
    #         invoices[reg.invoice_email] = {'invoice_email':reg.invoice_email,'invoice_number':reg.invoice_number, 'invoice_status':reg.invoice_status, 'invoice_date':reg.invoice_date, 'registrations':[]}
    #     invoices[reg.invoice_email]['registrations'].append(reg.id)
    return render_template('invoice_list.html', invoices=all_inv, back='canceled')

@bp.route('/all', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def all():
    if current_user.event_id:
        all_inv = Invoice.query.filter(Invoice.event_id == current_user.event_id).all()
    else:
        all_inv = Invoice.query.all()

    # invoices = {}
    # for reg in all_inv:
    #     if reg.invoice_email not in invoices:
    #         invoices[reg.invoice_email] = {'invoice_email':reg.invoice_email,'invoice_number':reg.invoice_number, 'invoice_status':reg.invoice_status, 'invoice_date':reg.invoice_date, 'invoice_total':0, 'registrations':[]}
    #     invoices[reg.invoice_email]['invoice_total'] += reg.total_due

    #     invoices[reg.invoice_email]['registrations'].append(reg.id)
    now = datetime.now()
    return render_template('invoice_list.html', invoices=all_inv, back='all', now=now)

@bp.route('/update', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def update():
    invnumber = request.args.get('invnumber')
    inv = get_inv(invnumber)
    if inv.invoice_type == 'REGISTRATION':
        regs = inv.regs
    elif inv.invoice_type == 'MERCHANT':
        regs = inv.merchants
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

        log_reg_action(reg, 'INVOICE UPDATED')

    return render_template('update_invoice.html', form=form, regs=regs, inv=inv)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def createinvoice():
    regids = request.args.get('regids')
    type = request.args.get('type')
    print(type)
    print('regids', regids)
    if type == 'REGISTRATION':
        regs = get_regs(regids)
        paypal_donation = 0
        registration_price = 0
        nmr_price = 0
        total_due = 0
        for reg in regs:
            paypal_donation += reg.paypal_donation
            registration_price += reg.registration_price
            nmr_price += reg.nmr_price
            total_due += reg.total_due
        form = SendInvoiceForm()
        form.paypal_donation.data = paypal_donation
        form.registration_amount.data = registration_price + nmr_price
        form.invoice_amount.data = total_due
        form.invoice_date.data = datetime.now()
        form.invoice_email.data = reg.invoice_email
    elif type == 'MERCHANT':
        regs = get_merchants(regids)
        processing_fee = 0
        space_fee = 0
        for merchant in regs:
            processing_fee += merchant.processing_fee
            space_fee += merchant.space_fee
        form = SendInvoiceForm()
        form.space_fee.data = space_fee
        form.processing_fee.data = processing_fee
        form.merchant_fee.data = space_fee + processing_fee
        form.invoice_date.data = datetime.now()
        form.invoice_email.data = merchant.email
    
    if request.method == 'POST':
        invoice_number = request.form.get('invoice_number')
        invoice_date = request.form.get('invoice_date')
        invoice_email = request.form.get('invoice_email')
        notes = request.form.get('notes')
        
        if invoice_number is not None and type == 'REGISTRATION':
            # Create a new invoice for the registrations
            inv = Invoice(
                invoice_type = 'REGISTRATION',
                invoice_number = invoice_number,
                invoice_email = invoice_email,
                invoice_date = invoice_date,
                invoice_status = 'OPEN',
                registration_total = registration_price,
                nmr_total = nmr_price,
                donation_total = paypal_donation,
                balance = total_due,
                notes = notes,
                event_id = regs[0].event_id,
            )
            for reg in regs:      
                reg.invoice_number = invoice_number

            db.session.add(inv)
            db.session.commit()
        
        elif invoice_number is not None and type == 'MERCHANT':
            # Create a new invoice for the merchant
            inv = Invoice(
                invoice_type = 'MERCHANT',
                invoice_number = invoice_number,
                invoice_email = invoice_email,
                invoice_date = invoice_date,
                invoice_status = 'OPEN',
                space_fee = space_fee,
                processing_fee = processing_fee,
                balance = space_fee + processing_fee,
                notes = notes,
                event_id = regs[0].event_id,
            )
            for reg in regs:      
                reg.invoice_number = invoice_number

            db.session.add(inv)
            db.session.commit()

        return redirect(url_for('invoices.unsent'))

    return render_template('create_invoice.html', form=form, regs=regs, type=type)

@bp.route('/payment', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def createpayment():
    invnumber = request.args.get('invnumber')
    inv = get_inv(invnumber)
    if inv.invoice_type == 'REGISTRATION':
        regs = inv.regs
    elif inv.invoice_type == 'MERCHANT':
        regs = inv.merchants

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
    
    if request.method == 'POST':
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
            # Create a new payment for the registrations
            payment_balance = payment_amount
            for reg in regs:
                regid = reg.id
                reg_balance = reg.balance
                if payment_balance > 0:
                    pay = Payment(
                        type = payment_type,
                        check_num = check_num if check_num != '' else None,
                        payment_date = payment_date,
                        # amount = payment_amount,
                        reg_id = regid,
                        invoice_number  = invoice_number,
                        event_id = reg.event_id
                    )
                    if reg_balance <= payment_balance:
                        payment_balance = payment_balance - reg_balance
                        pay.amount = reg_balance
                        pay.registration_amount = reg.registration_balance
                        pay.nmr_amount = reg.nmr_balance
                        pay.paypal_donation_amount = reg.paypal_donation_balance
                        reg.registration_balance = 0
                        reg.nmr_balance = 0
                        reg.paypal_donation_balance = 0
                    else:
                        # reg.balance = reg.balance - payment_balance
                        pay.amount = payment_balance

                        if payment_balance <= reg.registration_balance:
                            reg.registration_balance -= payment_balance
                            pay.registration_amount = payment_balance
                            payment_balance = 0
                        else:
                            payment_balance -= reg.registration_balance
                            reg.registration_balance = 0
                            pay.registration_amount =  reg.registration_balance
                        
                        if payment_balance <= reg.nmr_balance:
                            reg.nmr_balance -= payment_balance
                            pay.nmr_amount = payment_balance
                            payment_balance = 0
                        else:
                            payment_balance -= reg.nmr_balance
                            reg.nmr_balance = 0
                            pay.nmr_amount =  reg.nmr_balance

                        if payment_balance <= reg.paypal_donation_balance:
                            reg.paypal_donation_balance -= payment_balance
                            pay.paypal_donation_amount = payment_balance
                            payment_balance = 0
                        else:
                            payment_balance -= reg.paypal_donation_balance
                            reg.paypal_donation_balance = 0
                            pay.paypal_donation_amount =  reg.paypal_donation_balance

                    db.session.add(pay)
                    reg.notes = notes
                    reg.balance = recalculate_reg_balance(reg)
            inv.balance = inv.balance - payment_amount
            if inv.balance <= 0:
                inv.invoice_status = 'PAID'
            inv.notes = notes

            db.session.commit()

            log_reg_action(reg, 'INVOICE PAID')
        elif payment_amount is not None and inv.invoice_type == 'MERCHANT':
            # Create a new payment for the merchant
            payment_balance = payment_amount
            for reg in regs:
                regid = reg.id
                reg_balance = reg.merchant_fee
                if payment_balance > 0:
                    pay = Payment(
                        type = payment_type,
                        check_num = check_num if check_num != '' else None,
                        payment_date = payment_date,
                        # amount = payment_amount,
                        merchant_id = regid,
                        invoice_number  = invoice_number,
                        event_id = reg.event_id
                    )
                    if reg_balance <= payment_balance:
                        payment_balance = payment_balance - reg_balance
                        pay.space_fee_amount = reg.space_fee
                        pay.processing_fee_amount = reg.processing_fee
                        pay.amount = reg_balance
                        reg.space_fee_balance = 0
                        reg.processing_fee_balance = 0
                    else:
                        # reg.balance = reg.balance - payment_balance
                        pay.amount = payment_balance

                        if payment_balance <= reg.space_fee:
                            pay.space_fee_amount = payment_balance
                            reg.space_fee_balance -= payment_balance
                            payment_balance = 0
                            
                        else:
                            payment_balance -= reg.space_fee
                            pay.space_fee_amount = reg.space_fee
                            reg.space_fee_balance = 0
                        
                        if payment_balance <= reg.processing_fee:
                            pay.processing_fee_amount = payment_balance
                            reg.processing_fee_balance -= payment_balance
                            payment_balance = 0
                        else:
                            payment_balance -= reg.processing_fee
                            pay.processing_fee_amount = reg.processing_fee
                            reg.processing_fee_balance = 0

                    db.session.add(pay)
                    reg.notes = notes

            inv.balance = inv.balance - payment_amount
            if inv.balance <= 0:
                inv.invoice_status = 'PAID'
            inv.notes = notes

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