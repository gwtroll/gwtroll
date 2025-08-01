from flask import render_template
from app.users import bp

from flask_login import current_user, login_required
from flask_security import roles_accepted
from app.utils.security_utils import permission_required
from flask import render_template, request, flash, redirect, url_for
from app.forms import *
from app.models import *
from werkzeug.exceptions import abort
import uuid
from app.utils.db_utils import *

@bp.route('/', methods=('GET', 'POST'))
@login_required
@permission_required('view_users')
def users():

    if current_user.has_permission('admin'):
        users = User.query.order_by(User.lname).all()
    else:
        users = User.query.join(UserRoles, User.id==UserRoles.user_id).join(Role, UserRoles.role_id==Role.id).filter(Role.name != 'Admin').order_by(User.lname).all()

    return render_template('users.html', users=users)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
@permission_required('edit_users')
def createuser():

    form = CreateUserForm()
    form.role.choices = get_role_choices()
    form.department.choices = get_department_choices()
    
    if request.method == 'POST' and form.validate_on_submit():
        dup_user_check = User.query.filter(User.username == form.username.data.lower()).first()
        if dup_user_check:
            flash("Username Already Taken - Please Try Again",'error')
            return render_template('createuser.html', form=form)
        user = User()
        form.populate_object(user)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('users.users'))

    return render_template('createuser.html', form=form)

@bp.route('/<userid>/edit', methods=('GET', 'POST'))
@login_required
@permission_required('edit_users')
def edituser(userid):
    user = get_user(userid)
    if (not current_user.has_role('Admin')) and user.has_role('Admin'):
        return redirect(url_for('users.users'))
    form = EditUserForm()
    form.role.choices = get_role_choices()
    form.department.choices = get_department_choices()

    if request.method == 'POST' and form.validate_on_submit():
        form.populate_object(user)
        db.session.commit()
        return redirect(url_for('users.users'))
    

    form.populate_form(user)

    return render_template('edituser.html', user=user, form=form)

@bp.route('/<userid>/pwreset', methods=('GET', 'POST'))
@login_required
@permission_required('edit_users')
def pwresetuser(userid):
    user = get_user(userid)
    
    if (not current_user.has_role('Admin')) and user.has_role('Admin'):
        return redirect(url_for('users.users'))
    
    form = UpdatePasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for('users.users'))
    
    return render_template('pwresetuser.html', user=user, form=form)