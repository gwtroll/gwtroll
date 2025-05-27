from flask import render_template
from app.events import bp

from flask_login import login_required
from flask import render_template, request, redirect
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted

@bp.route('/', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def events():
    events = Event.query.all()
    return render_template('events.html', events=events)

@bp.route('/<eventid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def viewevent(eventid):
    event = Event.query.filter(Event.id==eventid).first()
    form = CreateEventForm(
        event_name=event.name,
        event_description=event.description,
        event_start=event.start_date,
        event_end=event.end_date,
        event_location=event.location
    )
    return render_template('event.html', event=event, form=form)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def createevent():
    form = CreateEventForm()
    if request.method == 'POST':
        new_event = Event(
            name=form.event_name.data,
            year=datetime.now().year,
            description=form.event_description.data,
            start_date=form.event_start.data,
            end_date=form.event_end.data,
            location=form.event_location.data,
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect('/')
    return render_template('createevent.html', form=form)