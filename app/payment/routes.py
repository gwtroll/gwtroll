from flask import render_template
from app.payment import bp

from flask_login import login_required
from flask import render_template, request, redirect, url_for
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from app.utils.security_utils import *

from flask_security import roles_accepted

@bp.route('/', methods=('GET', 'POST'))
@login_required
@permission_required('admin')
def payment():
    all_payments = Payment.query.order_by(Payment.id).all()
    return render_template('viewpayment.html', payments=all_payments)

# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# @permission_required('admin')
# def createkingdom():
#     form = KingdomForm()
#     if request.method == 'POST':
#         kingdom = Kingdom(
#             name=request.form.get('name'),
#         )
#         db.session.add(kingdom)
#         db.session.commit()
#         return redirect('/')
#     return render_template('createkingdom.html', form=form)

@bp.route('/<paymentid>', methods=('GET', 'POST'))
@login_required
@permission_required('admin')
def editpayment(paymentid):
    payment = Payment.query.get(paymentid)
    form = PaymentForm(
        type = payment.type,
        check_num = payment.check_num,
        payment_date = payment.payment_date,
        registration_amount = payment.registration_amount,
        nmr_amount = payment.nmr_amount,
        paypal_donation_amount = payment.paypal_donation_amount,
        space_fee_amount = payment.space_fee_amount,
        processing_fee_amount = payment.processing_fee_amount,
        rider_fee_amount = payment.rider_fee_amount,
        electricity_fee_amount = payment.electricity_fee_amount,
        amount = payment.amount,
        invoice_number = payment.invoice_number
    )
    if request.method == 'POST' and form.validate_on_submit():
        payment.type = form.type.data
        payment.check_num = form.check_num.data
        payment.registration_amount = form.registration_amount.data
        payment.nmr_amount = form.nmr_amount.data
        payment.paypal_donation_amount = form.paypal_donation_amount.data
        payment.space_fee_amount = form.space_fee_amount.data
        payment.processing_fee_amount = form.processing_fee_amount.data
        payment.rider_fee_amount = form.rider_fee_amount.data
        payment.electricity_fee_amount = form.electricity_fee_amount.data
        payment.invoice_number = form.invoice_number.data

        payment.amount = payment.registration_amount + payment.nmr_amount + payment.paypal_donation_amount + payment.space_fee_amount + payment.processing_fee_amount + payment.electricity_fee_amount + payment.rider_fee_amount

        db.session.commit()

        invoice = payment.invoice if payment.invoice is not None else None
        if invoice is not None:
            invoice.recalculate_balance()

        db.session.commit()

        return redirect(url_for('payment.payment'))
    if form.errors: print(form.errors)
    return render_template('editpayment.html', form=form, payment=payment)

@bp.route('/<paymentid>/delete', methods=('GET', 'POST'))
@login_required
@permission_required('admin')
def deletepayment(paymentid):
    payment = Payment.query.get(paymentid)
    
    if request.method == 'POST':
        invoice = payment.invoice if payment.invoice is not None else None
        registration = payment.reg if payment.reg is not None else None
        earlyon = payment.earlyonrequest if payment.earlyonrequest is not None else None
        merchant = payment.merchant if payment.merchant is not None else None
        db.session.delete(payment)
        db.session.commit()
        if invoice is not None:
            invoice.recalculate_balance()
        if registration is not None:
            registration.recalculate_balance()
        if earlyon is not None:
            earlyon.recalculate_balance()
        if merchant is not None:
            merchant.recalculate_balance()
        db.session.commit()
        return redirect(url_for('payment.payment'))
    return render_template('deletepayment.html', payment=payment)