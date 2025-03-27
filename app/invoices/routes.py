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
    all_regs = Registrations.query.filter(and_(Registrations.invoice_number == None, Registrations.prereg == True, Registrations.duplicate == False)).order_by(Registrations.invoice_email).all()
    # preregtotal = prereg_total()
    # invoicecount = unsent_count()
    # regcount = unsent_reg_count()
    invoices = {}
    for reg in all_regs:
        if reg.invoice_email not in invoices:
            invoices[reg.invoice_email] = {'invoice_email':reg.invoice_email,'invoice_number':reg.invoice_number, 'invoice_status':'UNSENT', 'invoice_date':None, 'registrations':[]}
        invoices[reg.invoice_email]['registrations'].append(reg.id)
    return render_template('unsent_list.html', invoices=invoices)

@bp.route('/open', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def open():
    all_inv = Invoice.query.filter(Invoice.invoice_status == 'OPEN').all()
    # all_regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.prereg == True, Registrations.invoice_status == 'OPEN')).order_by(Registrations.invoice_email).all()
    # preregtotal = prereg_total()
    # invoicecount = unsent_count()
    # regcount = unsent_reg_count()
    invoices = {}
    for inv in all_inv:
        if inv.invoice_email not in invoices:
            invoices[inv.invoice_email] = {'invoice_email':inv.invoice_email,'invoice_number':inv.invoice_number, 'invoice_status':inv.invoice_status, 'invoice_date':inv.invoice_date, 'registrations':[]}
        for reg in inv.regs:
            invoices[inv.invoice_email]['registrations'].append(reg.id)
    return render_template('open_list.html', invoices=invoices)

@bp.route('/paid', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def paid():
    all_inv = Invoice.query.filter(Invoice.invoice_status == 'PAID').all()
    # all_regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.prereg == True, Registrations.invoice_status == 'OPEN')).order_by(Registrations.invoice_email).all()
    # preregtotal = prereg_total()
    # invoicecount = unsent_count()
    # regcount = unsent_reg_count()
    invoices = {}
    for inv in all_inv:
        if inv.invoice_email not in invoices:
            invoices[inv.invoice_email] = {'invoice_email':inv.invoice_email,'invoice_number':inv.invoice_number, 'invoice_status':inv.invoice_status, 'invoice_date':inv.invoice_date, 'registrations':[]}
        for reg in inv.regs:
            invoices[inv.invoice_email]['registrations'].append(reg.id)
    return render_template('paid_list.html', invoices=invoices)

@bp.route('/canceled', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def canceled():
    all_regs = Registrations.query.filter(and_(Registrations.prereg == True, or_(Registrations.invoice_status == 'CANCELED', Registrations.invoice_status == 'DUPLICATE'))).order_by(Registrations.invoice_email).all()
    preregtotal = prereg_total()
    invoicecount = unsent_count()
    regcount = unsent_reg_count()
    invoices = {}
    for reg in all_regs:
        if reg.invoice_email not in invoices:
            invoices[reg.invoice_email] = {'invoice_email':reg.invoice_email,'invoice_number':reg.invoice_number, 'invoice_status':reg.invoice_status, 'invoice_date':reg.invoice_date, 'registrations':[]}
        invoices[reg.invoice_email]['registrations'].append(reg.id)
    return render_template('invoice_list.html', invoices=invoices, preregtotal=preregtotal, invoicecount=invoicecount, regcount=regcount, back='canceled')

@bp.route('/all', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def all():
    all_regs = Registrations.query.filter(Registrations.prereg == True).order_by(Registrations.invoice_email).all()
    invoices = {}
    for reg in all_regs:
        if reg.invoice_email not in invoices:
            invoices[reg.invoice_email] = {'invoice_email':reg.invoice_email,'invoice_number':reg.invoice_number, 'invoice_status':reg.invoice_status, 'invoice_date':reg.invoice_date, 'invoice_total':0, 'registrations':[]}
        invoices[reg.invoice_email]['invoice_total'] += reg.total_due

        invoices[reg.invoice_email]['registrations'].append(reg.id)
    now = datetime.now()
    return render_template('invoice_list.html', invoices=invoices, back='all', now=now)

@bp.route('/update', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def update():
    invnumber = request.args.get('invnumber')
    inv = get_inv(invnumber)
    regs = inv.regs
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

    return render_template('update_invoice.html', form=form, regs=regs)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def createinvoice():
    regids = request.args.get('regids')
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
    
    if request.method == 'POST':
        invoice_number = request.form.get('invoice_number')
        invoice_date = request.form.get('invoice_date')
        invoice_email = request.form.get('invoice_email')
        notes = request.form.get('notes')
        
        if invoice_number is not None:
            inv = Invoice(
                invoice_number = invoice_number,
                invoice_email = invoice_email,
                invoice_date = invoice_date,
                invoice_status = 'OPEN',
                registration_total = registration_price,
                nmr_total = nmr_price,
                donation_total = paypal_donation,
                balance = total_due,
                notes = notes
            )
            for reg in regs:      
                reg.invoice_number = invoice_number

            db.session.add(inv)
            db.session.commit()

            log_reg_action(reg, 'INVOICE SENT')
        return redirect(url_for('invoices.unsent'))

    return render_template('create_invoice.html', form=form, regs=regs)

@bp.route('/payment', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def createpayment():
    invnumber = request.args.get('invnumber')
    inv = get_inv(invnumber)
    regs = inv.regs

    form = PayInvoiceForm()
    form.invoice_amount.data = inv.invoice_total
    form.registration_amount.data = inv.registration_total
    form.invoice_number.data  = inv.invoice_number
    form.invoice_status.data  = inv.invoice_status
    form.paypal_donation.data  = inv.donation_total
    form.invoice_date.data  = inv.invoice_date
    form.notes.data  = inv.notes
    form.invoice_email.data = inv.invoice_email
    
    if request.method == 'POST':
        # payment_date = DateField('Payment Date')
        # payment_amount = IntegerField('Payment Amount')
        # payment_type = SelectField('Payment Type',choices=[('PAYPAL','PAYPAL'),('CHECK','CHECK')])
        # check_num = IntegerField('Check Number')

        invoice_number = request.form.get('invoice_number')
        payment_date = request.form.get('payment_date')
        payment_amount = int(request.form.get('payment_amount'))
        payment_type = request.form.get('payment_type')
        check_num = request.form.get('check_num')
        notes = request.form.get('notes')
        
        if payment_amount is not None:
            pay = Payment(
                type = payment_type,
                check_num = check_num if check_num != '' else None,
                payment_date = payment_date,
                amount = payment_amount,
                invoice_number  = invoice_number
            )
            
            inv.balance = inv.balance - pay.amount
            if inv.balance <= 0:
                inv.invoice_status = 'PAID'
            inv.notes = notes

            db.session.add(pay)
            db.session.commit()

        payment_balance = payment_amount
        for reg in regs:
            
            if reg.balance < payment_balance:
                payment_balance = payment_balance - reg.balance
                reg.balance = 0
            else:
                reg.balance = reg.balance - payment_balance
                payment_balance = 0
            log_reg_action(reg, 'INVOICE PAID')
        return redirect(url_for('invoices.open'))

    return render_template('create_payment.html', form=form, regs=regs)


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