from flask import render_template
from app.earlyon import bp
from app.utils.security_utils import *
from flask_login import current_user, login_required
from flask import render_template, request, url_for, flash, redirect
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from app.utils.email_utils import *
import math

from flask_security import roles_accepted
from markupsafe import Markup

@bp.route('/', methods=('GET',))
@login_required
@permission_required('earlyon_view')
def earlyon():
    if current_user.has_role('Autocrat') or current_user.has_role('Admin'):
        earlyons = EarlyOnRequest.query.all()
    elif current_user.has_role('Department Head'):
        earlyons = EarlyOnRequest.query.filter_by(department_id=current_user.department_id).all()
        if current_user.department.name == 'Land':
            earlyons = EarlyOnRequest.query.filter_by(department_id=current_user.department_id).all()
            for x in ['Land - Ansteorra','Land - Trimaris','Land Liaisons/Set-up Crews']:
                temp_dept = get_department_by_name(x)
                earlyons.extend(EarlyOnRequest.query.filter_by(department_id=temp_dept.id).all())
        if current_user.department.name == 'Merchant Coordinators':
            earlyons = EarlyOnRequest.query.filter_by(department_id=current_user.department_id).all()
            for x in ['Merchant/Vendor']:
                temp_dept = get_department_by_name(x)
                earlyons.extend(EarlyOnRequest.query.filter_by(department_id=temp_dept.id).all())

    return render_template('earlyon_list.html', earlyons=earlyons)

@bp.route('/<int:earlyon_id>', methods=('GET','POST'))
@login_required
@permission_required('earlyon_edit')
def update(earlyon_id):
    earlyon = EarlyOnRequest.query.get_or_404(earlyon_id)

    form = EarlyOnApprovalForm(
        arrival_date=earlyon.arrival_date.strftime('%Y/%m/%d'),
        department=earlyon.department_id,
        merchant=earlyon.merchant_id if earlyon.merchant_id else None,
        notes=earlyon.notes,
        dept_approval_status=earlyon.dept_approval_status,
        autocrat_approval_status=earlyon.autocrat_approval_status,
    )

    form.arrival_date.choices = get_earlyon_arrival_dates()
    form.department.choices = get_department_choices()
    form.merchant.choices = get_merchant_choices()

    current_dept_approval = earlyon.dept_approval_status
    current_autocrat_approval = earlyon.autocrat_approval_status

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.department.data == None:
                flash('Please select a department.', 'error')
                return render_template('edit_earlyon.html', form=form, earlyon=earlyon)
            earlyon.arrival_date = form.arrival_date.data
            earlyon.department_id = form.department.data
            earlyon.notes = form.notes.data
            earlyon.dept_approval_status = form.dept_approval_status.data
            earlyon.autocrat_approval_status = form.autocrat_approval_status.data

            if earlyon.dept_approval_status == 'APPROVED' and earlyon.autocrat_approval_status == 'APPROVED' and earlyon.rider_balance <= 0:
                earlyon.registration.early_on_approved = True
                earlyon.registration.expected_arrival_date = earlyon.arrival_date
                for rider in earlyon.earlyonriders:
                    rider.reg.early_on_approved = True
                    rider.reg.expected_arrival_date= earlyon.arrival_date

            if earlyon.dept_approval_status == 'APPROVED' and earlyon.autocrat_approval_status == 'APPROVED' and (current_dept_approval != 'APPROVED' or current_autocrat_approval != 'APPROVED'):
                regs = [earlyon.registration]
                for rider in earlyon.earlyonriders:
                    regs.append(rider.reg)
                send_earlyon_approval_email(earlyon.registration.email,regs)
                
            db.session.commit()
            return render_template('earlyon_list.html', earlyons=EarlyOnRequest.query.all())
        flash('There was an error with your submission. Please check the form and try again.', 'error')
        return render_template('edit_earlyon.html', form=form, earlyon=earlyon)
        
    if earlyon.earlyonriders:
        for rider in earlyon.earlyonriders:
            form.riders.append_entry(rider)
            
    return render_template('edit_earlyon.html', form=form, earlyon=earlyon)


@bp.route('/application/<int:regid>', methods=('GET', 'POST'))
def createearlyon(regid):
    # Close Merchants at Midnight MM/DD/YYYY
    # if datetime.now().date() >= datetime.strptime('02/22/2025','%m/%d/%Y').date():
    #     return render_template("prereg_closed.html")

    reg = Registrations.query.get_or_404(regid)

    if len(reg.earlyonrequests_ref) > 0 or len(reg.earlyonriders_ref) > 0:
        flash('You have perviously submitted an Early On Request or as a rider on another request.\nPlease contact your department head for more information.','error')
        return redirect(url_for('earlyon.success'))
    form = EarlyOnForm()
    form.arrival_date.choices = get_earlyon_arrival_dates()
    form.department.choices = get_department_choices()
    form.merchant.choices = get_merchant_choices()

    if request.method == 'POST':
        if form.department.data == 'None':
            flash('Please select a department.', 'error')
            return render_template('create_earlyon.html', form=form, reg=reg)
        if request.form.get('remove'):
            remove = request.form.get('remove')
            form.riders.entries.pop(int(remove))
            return render_template('create_earlyon.html', form=form, reg=reg)
        if form.validate_on_submit():
            if request.form.get('add'):
                form.riders.append_entry()
                return render_template('create_earlyon.html', form=form, reg=reg)

            rider_ids = []
            rider_registration_ids = []
            
            for idx, field in enumerate(form.riders):
                rider_ids.append(field.regid.data)

            rider_registrations = Registrations.query.filter(Registrations.id.in_(rider_ids)).all()
            for rider in rider_registrations:
                if len(rider.earlyonrequests_ref) > 0 or len(rider.earlyonriders_ref) > 0:
                    flash(f'Your rider Regid: {rider.id} - {rider.fname} {rider.lname} has perviously been submitted an Early On Request or as a rider on another request.\nPlease contact your department head for more information.','error')
                    return render_template('create_earlyon.html', form=form, reg=reg)
                else:
                    rider_registration_ids.append(rider.id)

            for id in rider_ids:
                if id not in rider_registration_ids:
                    flash(f"Rider with registration ID {id} does not exist.", 'error')
                    return render_template('create_earlyon.html', form=form, reg=reg)
                
            riders = []

            rider_cost = 0
            free_riders = 1
            adult_riders = 0
            merchant_dept = get_department_by_name('Merchant/Vendor')
            if int(form.department.data) == int(merchant_dept.id):
                free_riders = 3
                if form.merchant.data != None and form.merchant.data != '-':
                    merchant = get_merchant(form.merchant.data)
                    merchant_space = (int(merchant.frontage_width) + int(merchant.ropes_left) + int(merchant.ropes_right)) * (int(merchant.frontage_depth) + int(merchant.ropes_front) + int(merchant.ropes_back))
                    merchant_space = merchant_space - merchant.personal_space if merchant.personal_space != None and merchant.personal_space > 0 else merchant_space
                    if merchant_space > 0:
                        free_riders = math.ceil(merchant_space/600) * 3

            for idx, field in enumerate(form.riders):

                if field.minor.data == False:
                    adult_riders += 1
                    if adult_riders > free_riders:
                        rider_cost += 15
                
                earlyon_rider = EarlyOnRider(
                    fname=field.fname.data,
                    lname=field.lname.data,
                    scaname=field.scaname.data,
                    minor= field.minor.data,
                    regid=field.regid.data,
                )

                riders.append(earlyon_rider)            
                db.session.add_all(riders)

            earlyon = EarlyOnRequest(
                reg_id = reg.id,
                arrival_date=form.arrival_date.data,
                department_id=form.department.data,
                merchant_id = form.merchant.data,
                notes=form.notes.data,
                dept_approval_status='PENDING',
                autocrat_approval_status='PENDING',
                earlyonriders=riders,
            )
            if rider_cost > 0:
                earlyon.rider_cost = rider_cost
                earlyon.rider_balance = rider_cost

            db.session.add(earlyon)
            db.session.commit()

            regs = [reg]
            for rider in earlyon.earlyonriders:
                r = get_reg(rider.regid)
                regs.append(r)

            send_earlyon_confirmation_email(reg.email,regs, earlyon.arrival_date)
            approval_notification_recipients = get_approval_notification_recipients(earlyon.department_id)
            send_earlyon_approval_notification_email(approval_notification_recipients, regs, earlyon.id, earlyon.arrival_date)
            
            return redirect(url_for('earlyon.success', earlyonid=earlyon.id))
    return render_template('create_earlyon.html', form=form, reg=reg)

@bp.route('/success')
def success():
    earlyonid = request.args.get('earlyonid')
    return render_template('earlyon_success.html', earlyonid=earlyonid)