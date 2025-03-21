from flask import render_template
from app.roles import bp

from flask_login import login_required
from flask import render_template, request, redirect
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def createrole():
    form = CreateRoleForm()
    all_roles = Role.query.filter(Role.id is not None).all()
    if request.method == 'POST':
        role = Role(id = request.form.get('id') ,name=request.form.get('role_name'))
        db.session.add(role)
        db.session.commit()
        return redirect('/')
    return render_template('createrole.html', form=form, roles=all_roles)