from flask import render_template
from app.recruitment import bp
from app.utils.security_utils import *
from flask_login import current_user, login_required
from flask import render_template, request, url_for, flash, redirect
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted
from markupsafe import Markup

@bp.route('/', methods=('GET',))
def recruitmentschedule():
    if current_user.department.name == 'Recruitment' or current_user.has_permission('admin'):
        timeslots = RecruitmentSchedule.query.filter().order_by(RecruitmentSchedule.start_datetime).all()
    else:
        timeslots = RecruitmentSchedule.query.filter(RecruitmentSchedule.volunteer_id==None).order_by(RecruitmentSchedule.start_datetime).all()
    return render_template('recruitmenttimeslot_list.html', timeslots=timeslots)

@bp.route('/<int:departmentid>', methods=('GET',))
def recruitmentschedule_dept(departmentid):
    timeslots = RecruitmentSchedule.query.filter(RecruitmentSchedule.department_id==departmentid).order_by(RecruitmentSchedule.start_datetime).all()
    return render_template('recruitmenttimeslot_list.html', timeslots=timeslots)

@bp.route('/timeslot/<int:recruitmentscheduleid>', methods=('GET',))
def recruitmentschedule_item(recruitmentscheduleid):
    signup_form = VolunteerSignupForm()
    signup_form.kingdom.choices = get_kingdom_choices()
    signup_form.lodging.choices = get_lodging_choices()
    timeslot = RecruitmentSchedule.query.get_or_404(recruitmentscheduleid)
    return render_template('view_recruitmenttimeslot.html', timeslot=timeslot, signup_form=signup_form)

# @bp.route('/myschedule', methods=('GET',))
# @login_required
# def myrecruitmentschedule():
#     timeslots = current_user.recruitmentschedules
#     return render_template('myvolunteerschedule.html', timeslots=timeslots)

@bp.route('/recruitmentschedule/<int:recruitmentscheduleid>/add', methods=('','POST'))
def addrecruitmentschedule(recruitmentscheduleid):
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    scaname = request.form.get('scaname')
    lodging = request.form.get('lodging')
    kingdom = request.form.get('kingdom')
    timeslot = RecruitmentSchedule.query.get_or_404(int(recruitmentscheduleid))
    if timeslot.volunteer_id == None:
        vol = Volunteer(
            fname=fname,
            lname=lname,
            scaname=scaname,
            lodging_id=lodging,
            kingdom_id=kingdom
        )
        db.session.add(vol)
        db.session.commit()
        timeslot.volunteer_id = vol.id
        db.session.commit()
    return redirect(url_for('recruitment.recruitmentschedule'))

@bp.route('/recruitmentschedule/<int:recruitmentscheduleid>/delete', methods=('','POST'))
@login_required
# @permission_required('scheduledevents_edit')
def removerecruitmentschedule(recruitmentscheduleid):
    timeslot = RecruitmentSchedule.query.get_or_404(recruitmentscheduleid)
    timeslot.volunteer_id = None
    db.session.commit()
    return redirect(url_for('recruitment.recruitmentschedule'))

@bp.route('/<int:recruitmentscheduleid>/edit', methods=('GET','POST'))
@login_required
# @permission_required('scheduledevents_edit')
def updaterecruitmentschedule(recruitmentscheduleid):
    timeslot = RecruitmentSchedule.query.get_or_404(recruitmentscheduleid)
    form = RecruitmentScheduleForm()
    form.volunteerposition.choices = get_volunteerposition_choices()
    form.department.choices = get_volunteerdepartment_choices()

    if request.method == 'POST' and form.validate_on_submit():
        form.populate_object(timeslot)
        db.session.commit()
        return redirect(url_for('recruitment.recruitmentschedule_dept',departmentid=current_user.department_id))
    form.populate_form(timeslot)
    return render_template('edit_recruitmenttimeslot.html', form=form, timeslot=timeslot)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
# @permission_required('scheduledevents_edit')
def createrecruitmentschedule():

    form = RecruitmentScheduleForm()
    form.volunteerposition.choices = get_volunteerposition_choices()
    form.department.choices = get_volunteerdepartment_choices()

    if request.method == 'POST':
        timeslot = RecruitmentSchedule()
        form.populate_object(timeslot)
        db.session.add(timeslot)

        db.session.commit()

        return redirect(url_for('recruitment.recruitmentschedule'))
    return render_template('create_recruitmenttimeslot.html', form=form)

@bp.route('/positions', methods=('GET', ''))
@login_required
# @permission_required('scheduledevents_edit')
def positions():

    if current_user.department.name == 'Recruitment' or current_user.has_permission('admin'):
        positions = VolunteerPosition.query.all()
    elif current_user.department_id != None:
        positions = VolunteerPosition.query.filter(VolunteerPosition.department_id==current_user.department_id).all()
    else:
        positions = None
    return render_template('positions_list.html', positions=positions)

@bp.route('/position/create', methods=('GET', 'POST'))
@login_required
# @permission_required('scheduledevents_edit')
def createposition():

    form = VolunteerPositionForm()
    form.department.choices = get_volunteerdepartment_choices()

    if request.method == 'POST':
        position = VolunteerPosition()
        form.populate_object(position)
        db.session.add(position)

        db.session.commit()

        return redirect(url_for('recruitment.positions'))
    return render_template('create_position.html', form=form)

@bp.route('/position/<positionid>/edit', methods=('GET', 'POST'))
@login_required
# @permission_required('scheduledevents_edit')
def editposition(positionid):

    position = get_position(positionid)
    form = VolunteerPositionForm()
    form.department.choices = get_volunteerdepartment_choices()

    if request.method == 'POST':
        position = VolunteerPosition()
        form.populate_object(position)
        db.session.add(position)

        db.session.commit()
        return redirect(url_for('recruitment.positions'))
    
    form.populate_form()

    return render_template('create_position.html', form=form)

@bp.route('/volunteer/<int:volid>', methods=('GET',))
def viewvolunteer(volid):
    form = VolunteerSignupForm()
    form.lodging.choices = get_lodging_choices()
    form.kingdom.choices = get_kingdom_choices()
    vol = Volunteer.query.filter(Volunteer.id==volid).first()
    if request.method == 'POST':
        form.populate_object(vol)
        db.session.commit()
        if current_user.department.name == 'Recruitment' or current_user.has_permission('admin'):
            return redirect(url_for('recruitment.recruitmentschedule'))
        else:
            return redirect(url_for('recruitment.recruitmentschedule_dept',departmentid=current_user.department_id))
    form.populate_form(vol)
    return render_template('view_volunteer.html', form=form)