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
@login_required
def recruitmentschedule():
    timeslots = RecruitmentSchedule.query.order_by(RecruitmentSchedule.start_datetime).all()
    return render_template('recruitmenttimeslot_list.html', timeslots=timeslots)

@bp.route('/<int:departmentid>', methods=('GET',))
@login_required
def recruitmentschedule_dept(departmentid):
    timeslots = RecruitmentSchedule.query.filter(RecruitmentSchedule.department_id==departmentid).order_by(RecruitmentSchedule.start_datetime).all()
    return render_template('recruitmenttimeslot_list.html', timeslots=timeslots)

@bp.route('/timeslot/<int:recruitmentscheduleid>', methods=('GET',))
@login_required
def recruitmentschedule_item(recruitmentscheduleid):
    timeslot = RecruitmentSchedule.query.get_or_404(recruitmentscheduleid)
    return render_template('view_recruitmenttimeslot.html', timeslot=timeslot)

@bp.route('/myschedule', methods=('GET',))
@login_required
def myrecruitmentschedule():
    timeslots = current_user.recruitmentschedules
    return render_template('myvolunteerschedule.html', timeslots=timeslots)

@bp.route('/<int:recruitmentscheduleid>/edit', methods=('GET','POST'))
@login_required
# @permission_required('scheduledevents_edit')
def updaterecruitmentschedule(recruitmentscheduleid):
    timeslot = RecruitmentSchedule.query.get_or_404(recruitmentscheduleid)
    form = RecruitmentScheduleForm()
    form.volunteer.choices = get_volunteer_choices()
    form.volunteerposition.choices = get_volunteerposition_choices()
    form.department.choices = get_department_choices()

    if request.method == 'POST' and form.validate_on_submit():
        form.populate_object(timeslot)
        db.session.commit()
    form.populate_form()
    return render_template('edit_earlyon.html', form=form, timeslot=timeslot)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
# @permission_required('scheduledevents_edit')
def createrecruitmentschedule():

    form = RecruitmentScheduleForm()
    form.volunteer.choices = get_volunteer_choices()
    form.volunteerposition.choices = get_volunteerposition_choices()
    form.department.choices = get_department_choices()

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

    positions = VolunteerPosition.query.all()
    return render_template('positions_list.html', positions=positions)

@bp.route('/position/create', methods=('GET', 'POST'))
@login_required
# @permission_required('scheduledevents_edit')
def createposition():

    form = VolunteerPositionForm()
    form.department.choices = get_department_choices()

    if request.method == 'POST':
        position = VolunteerPosition()
        form.populate_object(position)
        db.session.add(position)

        db.session.commit()

        return redirect(url_for('recruitment.positions'))
    return render_template('create_position.html', form=form)