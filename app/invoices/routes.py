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
    regs = Registrations.query.filter(and_(Registrations.invoice_number == None, Registrations.invoice_status != 'CANCELED', Registrations.invoice_status != 'DUPLICATE', Registrations.invoice_status != 'SENT', Registrations.invoice_status != 'PAID', Registrations.prereg_status == "SUCCEEDED")).order_by(Registrations.invoice_email).all()
    preregtotal = prereg_total()
    invoicecount = unsent_count()
    regcount = unsent_reg_count()
    return render_template('invoice_list.html', regs=regs, preregtotal=preregtotal, invoicecount=invoicecount, regcount=regcount, back='unsent')

@bp.route('/open', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def open():
    regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.prereg_status == "SUCCEEDED", Registrations.invoice_status == 'SENT')).order_by(Registrations.invoice_email).all()
    preregtotal = prereg_total()
    invoicecount = open_count()
    regcount = open_reg_count()
    return render_template('invoice_list.html', regs=regs, preregtotal=preregtotal, invoicecount=invoicecount, regcount=regcount, back='open')

@bp.route('/paid', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def paid():
    regs = Registrations.query.filter(and_(Registrations.invoice_number != None, Registrations.prereg_status == "SUCCEEDED", Registrations.invoice_status == 'PAID')).order_by(Registrations.invoice_email).all()
    preregtotal = prereg_total()
    invoicecount = paid_count()
    regcount = paid_reg_count()
    return render_template('invoice_list.html', regs=regs, preregtotal=preregtotal, invoicecount=invoicecount, regcount=regcount, back='paid')

@bp.route('/canceled', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def canceled():
    regs = Registrations.query.filter(and_(Registrations.prereg_status == "SUCCEEDED", or_(Registrations.invoice_status == 'CANCELED', Registrations.invoice_status == 'DUPLICATE'))).order_by(Registrations.invoice_email).all()
    preregtotal = prereg_total()
    invoicecount = canceled_count()
    regcount = canceled_reg_count()
    return render_template('invoice_list.html', regs=regs, preregtotal=preregtotal, invoicecount=invoicecount, regcount=regcount, back='canceled')

@bp.route('/all', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def all():
    regs = Registrations.query.filter(Registrations.prereg_status == "SUCCEEDED").order_by(Registrations.invoice_email).all()
    now = datetime.now()
    return render_template('invoice_list.html', regs=regs, back='all', now=now)

@bp.route('/<int:regid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Invoices','Department Head')
def update(regid):
    back = request.args.get('back')
    reg = get_reg(regid)
    form = UpdateInvoiceForm()
    form.price_paid.data = reg.price_paid
    form.price_calc.data = reg.price_calc
    form.paypal_donation_amount.data = reg.paypal_donation_amount
    form.price_due.data = reg.price_due
    form.invoice_number.data = reg.invoice_number
    form.invoice_paid.data = reg.invoice_paid
    if reg.invoice_date is not None:
        form.invoice_date.data = reg.invoice_date
    else:
        form.invoice_date.data = datetime.now()
    form.invoice_canceled.data = reg.invoice_canceled
    form.invoice_payment_date.data = reg.invoice_payment_date
    form.duplicate_invoice.data = True if reg.invoice_status == 'DUPLICATE' else False
    form.is_check.data = True if reg.pay_type == 'check' else False
    form.notes.data = reg.notes
    
    if request.method == 'POST':
        invoice_number = request.form.get('invoice_number')
        price_paid = int(request.form.get('price_paid'))
        price_calc = int(request.form.get('price_calc'))
        invoice_date = request.form.get('invoice_date')
        invoice_payment_date = request.form.get('invoice_payment_date')
        invoice_canceled = bool(request.form.get('invoice_canceled'))

        #if is_duplicate_invoice_number(invoice_number, reg):
        #    flash('Duplicate Invoice Number {}'.format(
        #    invoice_number))
        #    return render_template('update_invoice.html', reg=reg, form=form)
        
        if invoice_number is not None and invoice_number != '':
            reg.invoice_status = 'SENT'
        if int(price_paid) >= int(price_calc) + int(reg.paypal_donation_amount):
            reg.invoice_status = 'PAID'
        if bool(request.form.get('invoice_canceled')) == True:
            reg.invoice_status = 'CANCELED'
        if bool(request.form.get('duplicate_invoice')) == True:
            reg.invoice_status = 'DUPLICATE'

        reg.price_paid = price_paid
        reg.price_calc = price_calc
        if invoice_number != None and invoice_number != '':          
            reg.invoice_number = invoice_number

        if invoice_date != '' and invoice_date is not None:
            reg.invoice_date = invoice_date
        if invoice_payment_date != '' and invoice_payment_date is not None:
            reg.invoice_payment_date = invoice_payment_date

        reg.invoice_canceled = invoice_canceled

        reg.price_due = (price_calc + reg.paypal_donation_amount) - price_paid

        if bool(request.form.get('is_check')) == True:
            reg.pay_type = 'check'
        else:
            reg.pay_type = 'paypal'
        
        reg.notes = request.form.get('notes')

        db.session.commit()

        log_reg_action(reg, 'INVOICE UPDATED')

        match back:
            case 'unsent': 
                return redirect(url_for('invoices.unsent'))
            case 'open': 
                return redirect(url_for('invoices.open'))
            case 'paid': 
                return redirect(url_for('invoices.paid'))
            case 'canceled': 
                return redirect(url_for('invoices.canceled'))
            case 'all': 
                return redirect(url_for('invoices.all'))
            case _:
                return redirect('/')


    return render_template('update_invoice.html', reg=reg, form=form)
