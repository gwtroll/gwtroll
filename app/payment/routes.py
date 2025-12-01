from flask import render_template, jsonify
from app.payment import bp

from flask_login import login_required
from flask import render_template, request, redirect, url_for
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from app.utils.security_utils import *
from app.utils.email_utils import *
from app.utils.paypal_api import verify_webhook_signature

from flask_security import roles_accepted

@bp.route('/', methods=('GET', 'POST'))
@login_required
@permission_required('admin')
def payment():
    all_payments = Payment.query.order_by(Payment.id).all()
    return render_template('viewpayment.html', payments=all_payments)

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

@bp.route('/paypal', methods=('', 'POST'))
def paypalpayment():
    try:
        data = request.get_json()
        auth_algo = request.headers.get('PAYPAL-AUTH-ALGO')
        cert_url = request.headers.get('PAYPAL-CERT-URL')
        transmission_id = request.headers.get('PAYPAL-TRANSMISSION-ID')
        transmission_sig = request.headers.get('PAYPAL-TRANSMISSION-SIG')
        transmission_time = request.headers.get('PAYPAL-TRANSMISSION-TIME')

        if verify_webhook_signature(auth_algo, cert_url, transmission_id, transmission_sig, transmission_time, data) == False:
            return jsonify({"message": "Webhook Unverified"}), 200
        invoice_data = None
        payment_data = None
        #Check if invoice in data
        if 'invoice' in data['resource']:
            invoice_data = data['resource']['invoice']
            #Check if payments in invoice
            if 'payments' in invoice_data:
                payment_data = data['resource']['invoice']['payments']['transactions']

        if data['event_type'] == "INVOICING.INVOICE.PAID" and invoice_data is not None:
            inv = Invoice.query.filter(Invoice.invoice_id==data['resource']['invoice']['id']).first()
            if inv is not None and payment_data is not None:
                for payment in payment_data:
                    payment_check = Payment.query.filter(Payment.paypal_id==payment['payment_id']).first()
                    if payment_check is None:
                        payment_amount = float(payment['amount']['value'])
                        invoice_number = inv.invoice_number
                        payment_date = datetime.strptime(payment['payment_date'],'%Y-%m-%d').date()
                        if inv.invoice_type == 'REGISTRATION':
                            regs = []
                            for r in inv.regs:
                                if r.duplicate != True and r.canceled != True:
                                    regs.append(r)
                        elif inv.invoice_type == 'MERCHANT':
                            regs = inv.merchants
                        elif inv.invoice_type == 'EARLYON':
                            regs = inv.earlyonrequests
                        if payment_amount is not None and inv.invoice_type == 'REGISTRATION':
                            payment_balance = payment_amount
                            for reg in regs:
                                if payment_balance > 0 and reg.balance > 0:
                                    pay = Payment(
                                        paypal_id = payment['payment_id'],
                                        type = 'PAYPAL',
                                        payment_date = payment_date,
                                        reg_id = reg.id,
                                        reg = reg,
                                        invoice_number = invoice_number,
                                    )
                                    pay.calculate_payment_amounts(payment_balance)
                                    db.session.add(pay)
                                    payment_balance -= (reg.registration_balance + reg.nmr_balance + reg.paypal_donation_balance)
                                    reg.recalculate_balance()
                                    db.session.commit()

                            inv.balance = float(inv.balance) - float(payment_amount)
                            if inv.balance <= 0:
                                inv.invoice_status = 'PAID'
                                for r in inv.regs:
                                    if r.duplicate == True or r.canceled == True:
                                        r.invoice_number = None
                                    else:
                                        send_fastpass_email(r.email, r)

                            db.session.commit()

                        elif payment_amount is not None and inv.invoice_type == 'MERCHANT':
                            payment_balance = payment_amount
                            for reg in regs:
                                if payment_balance > 0:
                                    pay = Payment(
                                        paypal_id = payment['payment_id'],
                                        type = 'PAYPAL',
                                        payment_date = payment_date,
                                        merchant_id = reg.id,
                                        merchant = reg,
                                        invoice_number  = invoice_number,
                                    )

                                    pay.calculate_payment_amounts(payment_balance)
                                    db.session.add(pay)
                                    payment_balance -= (float(reg.space_fee_balance) + reg.processing_fee_balance + float(reg.electricity_balance))
                                    reg.recalculate_balance()
                                    db.session.commit()

                            inv.balance = float(inv.balance) - float(payment_amount)
                            if inv.balance <= 0:
                                inv.invoice_status = 'PAID'

                            db.session.commit()

                        elif payment_amount is not None and inv.invoice_type == 'EARLYON':
                            payment_balance = payment_amount
                            for reg in regs:
                                if payment_balance > 0:
                                    pay = Payment(
                                        paypal_id = payment['payment_id'],
                                        type = 'PAYPAL',
                                        payment_date = payment_date,
                                        earlyonrequest_id = reg.id,
                                        earlyonrequest = reg,
                                        invoice_number  = invoice_number,
                                    )
                                    pay.calculate_payment_amounts(payment_balance)
                                    db.session.add(pay)
                                    payment_balance -= reg.rider_balance
                                    reg.recalculate_balance()
                                    db.session.commit()

                            inv.recalculate_balance()
                            if inv.balance <= 0:
                                inv.invoice_status = 'PAID'
                                #TODO: CREATE EARLY ON EMAIL

                            if reg.rider_balance <= 0 and reg.dept_approval_status == 'APPROVED' and reg.autocrat_approval_status == 'APPROVED':
                                reg.registration.early_on_approved = True
                                for rider in reg.earlyonriders:
                                    rider.reg.early_on_approved = True

                            db.session.commit()
        print(data)
        return jsonify({"message": "Operation successful"}), 200
    except Exception as e:
        send_webhook_error_email(str(e))
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500