from flask import render_template
from app.scheduledevents import bp
from app.utils.security_utils import *
from flask_login import current_user, login_required
from flask import render_template, request, url_for, flash, redirect
from app.forms import *
from app.models import *
from app.utils.db_utils import *
from app.utils.email_utils import *

from flask_security import roles_accepted
from markupsafe import Markup

@bp.route('/', methods=('GET',))
@login_required
def scheduledevents():
    scheduledevents = get_scheduledevents()
    return render_template('scheduledevents_list.html', scheduledevents=scheduledevents)

@bp.route('/<int:scheduledeventid>', methods=('GET',))
@login_required
def scheduledevent(scheduledeventid):
    scheduledevent = ScheduledEvent.query.get_or_404(scheduledeventid)
    return render_template('view_scheduledevent.html', scheduledevent=scheduledevent)

@bp.route('/myschedule', methods=('GET',))
@login_required
def myschedule():
    scheduledevents = current_user.scheduled_events
    print(scheduledevents)
    return render_template('myschedule.html', scheduledevents=scheduledevents)

@bp.route('/<int:scheduledeventid>/edit', methods=('GET','POST'))
@login_required
# @permission_required('scheduledevents_edit')
def updatescheduledevent(scheduledeventid):
    scheduledevent = ScheduledEvent.query.get_or_404(scheduledeventid)
    form = ScheduledEventForm()
    form.topic.choices = get_topic_choices()
    form.tags.choices = get_tag_choices()
    form.user_instructor.choices = get_user_instructor_choices()

    if request.method == 'POST' and form.validate_on_submit():
        form.populate_object(scheduledevent)
        db.session.commit()
    form.populate_form()
    return render_template('edit_earlyon.html', form=form, scheduledevent=scheduledevent)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
# @permission_required('scheduledevents_edit')
def createscheduledevent():

    form = ScheduledEventForm()
    form.topic.choices = get_topic_choices()
    form.tags.choices = get_tag_choices()
    form.user_instructor.choices = get_user_instructor_choices()

    if request.method == 'POST':
        if request.form.get('removetag'):
            remove = request.form.get('removetag')
            form.new_tag.entries.pop(int(remove))
            return render_template('create_scheduledevent.html', form=form)
        if request.form.get('removetopic'):
            remove = request.form.get('removetopic')
            form.new_topic.entries.pop(int(remove))
            return render_template('create_scheduledevent.html', form=form)
        if request.form.get('addtag'):
            form.new_tag.append_entry()
            return render_template('create_scheduledevent.html', form=form)
        if request.form.get('addtopic'):
            form.new_topic.append_entry()
            return render_template('create_scheduledevent.html', form=form)
        if form.validate_on_submit():

            new_tags = []
            new_topics = []
            
            for idx, field in enumerate(form.new_tag):
                if field.tag_name.data:
                    new_tag = Tag(name=field.tag_name.data)
                    new_tags.append(new_tag)
            for idx, field in enumerate(form.new_topic):
                if field.topic_name.data:
                    new_topic = Topic(name=field.topic_name.data)
                    new_topics.append(new_topic)

            db.session.add_all(new_tags)
            db.session.add_all(new_topics)

            db.session.commit()

            scheduled_event = ScheduledEvent()
            form.populate_object(scheduled_event)
            db.session.add(scheduled_event)

            for tag in new_tags:
                scheduled_event.tags.append(tag)
            for topic in new_topics:
                scheduled_event.topic_id = topic.id

            db.session.commit()

            return redirect(url_for('scheduledevents.scheduledevents'))
    return render_template('create_scheduledevent.html', form=form)