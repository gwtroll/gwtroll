from flask import render_template
from app.lodging import bp

from flask_login import login_required
from flask import render_template, request, redirect, url_for
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted

@bp.route('/', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def lodging():

    all_lodging = Lodging.query.order_by(Lodging.name).all()
    return render_template('viewlodging.html', lodgings=all_lodging)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def createlodging():
    form = LodgingForm()
    # form.event.choices = get_event_choices()
    if request.method == 'POST':
        lodging = Lodging(
            name=request.form.get('name'),
            # event_id=request.form.get('event'),
        )
        db.session.add(lodging)
        db.session.commit()
        return redirect('/')
    return render_template('createlodging.html', form=form)

@bp.route('/upload', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def uploadlodging():
    form = StandardUploadForm()
    # form.event.choices = get_event_choices()
    if request.method == 'POST':
        file = request.files['file']
        if file:
            for line in file.stream:
                line_content = line.decode('utf-8').strip()
                if line_content != 'Group Name':
                    group_name = line_content.split(',')[0].strip()
                    lodging = Lodging(
                        name=group_name,
                        # event_id=request.form.get('event'),
                    )
                    db.session.add(lodging)
                print(line_content)
        db.session.commit()
        return redirect(url_for('lodging.lodging'))

    return render_template('uploadlodging.html', form=form)

@bp.route('/<lodgingid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def editlodging(lodgingid):
    lodging = Lodging.query.get(lodgingid)
    form = LodgingForm(
        name=lodging.name,
        # event=lodging.event_id,
    )
    # form.event.choices = get_event_choices()
    form.submit.label.text = 'Update Lodging'
    if request.method == 'POST':
        lodging.name = request.form.get('name')
        # lodging.event_id = request.form.get('event')
        db.session.commit()
        return redirect(url_for('lodging.lodging'))
    return render_template('editlodging.html', form=form, lodging=lodging)

@bp.route('/<lodgingid>/delete', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def deletelodging(lodgingid):
    lodging = Lodging.query.get(lodgingid)

    if request.method == 'POST':
        db.session.delete(lodging)
        db.session.commit()
        return redirect(url_for('lodging.lodging'))
    return render_template('deletelodging.html', lodging=lodging)