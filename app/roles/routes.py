from flask import render_template
from app.roles import bp

from flask_login import login_required
from flask import render_template, request, redirect
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted

@bp.route('/', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def roles():
    all_roles = Role.query.filter(Role.id is not None).order_by(Role.id).all()
    return render_template('roles.html', roles=all_roles)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def createrole():
    form = CreateRoleForm()
    form.permissions.choices = get_permission_choices()
    all_roles = Role.query.filter(Role.id is not None).all()
    if request.method == 'POST':
        role = Role(id = request.form.get('id') ,name=request.form.get('role_name'))
        for permissionid in request.form.getlist('permissions'):
            role.permissions.append(get_permission(permissionid))
        db.session.add(role)
        db.session.commit()
        return redirect('/roles')
    return render_template('createrole.html', form=form, roles=all_roles)

@bp.route('/edit/<int:roleid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def editrole(roleid):
    role = Role.query.filter(Role.id == roleid).first()

    permission_array = []
    for permission in role.permissions:
        permission_array.append(permission.id)

    form = CreateRoleForm(
        id = role.id,
        role_name = role.name,
        permissions = permission_array
    )

    form.permissions.choices = get_permission_choices()

    if request.method == 'POST':
        role.id = request.form.get('id'),
        role.name=request.form.get('role_name')
        for permissionid in request.form.getlist('permissions'):
            role.permissions.append(get_permission(permissionid))
        db.session.commit()
        return redirect('/roles')
    return render_template('editrole.html', form=form)