from flask import render_template
from app.kingdom import bp

from flask_login import login_required
from flask import render_template, request, redirect, url_for
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted

@bp.route('/', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def kingdom():
    all_kingdom = Kingdom.query.order_by(Kingdom.name).all()
    print(all_kingdom)
    return render_template('viewkingdom.html', kingdoms=all_kingdom)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def createkingdom():
    form = KingdomForm()
    if request.method == 'POST':
        kingdom = Kingdom(
            name=request.form.get('name'),
        )
        db.session.add(kingdom)
        db.session.commit()
        return redirect('/')
    return render_template('createkingdom.html', form=form)

@bp.route('/upload', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def uploadkingdom():
    form = StandardUploadForm()
    if request.method == 'POST':
        file = request.files['file']
        if file:
            for line in file.stream:
                line_content = line.decode('utf-8').strip()
                if line_content != 'Kingdoms':
                    kingdom_name = line_content.split(',')[0].strip()
                    kingdom = Kingdom(
                        name=kingdom_name,
                    )
                    db.session.add(kingdom)
                print(line_content)
        db.session.commit()
        return redirect(url_for('kingdom.kingdom'))

    return render_template('uploadkingdom.html', form=form)

@bp.route('/<kingdomid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def editkingdom(kingdomid):
    kingdom = Kingdom.query.get(kingdomid)
    form = KingdomForm(
        name=kingdom.name,
    )
    form.submit.label.text = 'Update Kingdom'
    if request.method == 'POST':
        kingdom.name = request.form.get('name')
        db.session.commit()
        return redirect(url_for('kingdom.kingdom'))
    return render_template('editkingdom.html', form=form, kingdom=kingdom)

@bp.route('/<kingdomid>/delete', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def deletekingdom(kingdomid):
    kingdom = Kingdom.query.get(kingdomid)

    if request.method == 'POST':
        db.session.delete(kingdom)
        db.session.commit()
        return redirect(url_for('kingdom.kingdom'))
    return render_template('deletekingdom.html', kingdom=kingdom)