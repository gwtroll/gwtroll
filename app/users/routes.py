from flask import render_template
from app.users import bp

from flask_login import current_user, login_required
from flask_security import roles_accepted
from flask import render_template, request, flash, redirect
from app.forms import *
from app.models import *
from werkzeug.exceptions import abort
import uuid
from app.utils.db_utils import *

@bp.route('/', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Marshal Admin','Troll Shift Lead','Department Head')
def users():
    return_users = []
    if current_user.event_id:
        users = User.query.filter(User.event_id==current_user.event_id).order_by(User.lname).all()
    else:
        users = User.query.order_by(User.lname).all()
    if current_user.has_role('Admin'):
        return render_template('users.html', users=users)
    
    for user in users:
        if current_user.has_role('Marshal Admin') and user.has_role('Marshal User'):
            return_users.append(user)

        if (current_user.has_role('Troll Shift Lead') or current_user.has_role('Department Head')) and user.has_role('Troll User'):
            return_users.append(user)
        
        if current_user.has_role('Department Head') and user.has_role('Troll Shift Lead'):
            return_users.append(user)

    return render_template('users.html', users=return_users)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Marshal Admin','Troll Shift Lead','Department Head')
def createuser():

    form = CreateUserForm()
    form.role.choices = get_role_choices()
    form.event.choices = get_event_choices()
    
    if request.method == 'POST':
        dup_user_check = User.query.filter(User.username == form.username.data).first()
        if dup_user_check:
            flash("Username Already Taken - Please Try Again",'error')
            return render_template('createuser.html', form=form)
        user = User()
        user.username = form.username.data
        for roleid in form.role.data:
            user.roles.append(get_role(roleid))
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.medallion = form.medallion.data
        user.fs_uniquifier = uuid.uuid4().hex
        user.active = True
        user.event_id = form.event.data if form.event.data != 0 else None
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        db.session.close()

        return redirect('/users')

    return render_template('createuser.html', form=form)

@bp.route('/<userid>/edit', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Marshal Admin','Troll Shift Lead','Department Head')
def edituser(userid):
    user = get_user(userid)
    if not currentuser_has_permission_on_user(current_user,user):
        return redirect('/users')
    if not currentuser_has_permission_on_user(current_user,user):
        return redirect('/users')

    role_array = []
    for role in user.roles:
        role_array.append(role.id)

    form = EditUserForm(
        id = user.id, 
        username = user.username, 
        role = role_array,
        fname = user.fname,
        lname = user.lname,
        medallion = user.medallion,
        active = user.active,
        event = user.event_id
    )
    form.role.choices = get_role_choices()
    form.event.choices = get_event_choices()

    if request.method == 'POST':
        role_array = []
        for roleid in form.role.data:
            role_array.append(get_role(roleid))
        user = get_user(form.id.data)
        user.username = form.username.data
        user.roles = role_array
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.medallion = form.medallion.data
        user.medallion = form.medallion.data
        user.active = bool(request.form.get('active'))
        user.event_id = form.event.data if form.event.data != 0 else None

        db.session.commit()

        return redirect('/users')
    
    return render_template('edituser.html', user=user, form=form)

@bp.route('/<userid>/pwreset', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Marshal Admin','Troll Shift Lead','Department Head')
def pwresetuser(userid):
    user = get_user(userid)
    if not currentuser_has_permission_on_user(current_user,user):
        return redirect('/users')
    if not currentuser_has_permission_on_user(current_user,user):
        return redirect('/users')
    edit_request = request.args.get("submitValue")
        
    form = UpdatePasswordForm(
        id = user.id, 
        username = user.username, 
        password = ''
    )

    if request.method == 'POST':
        user = get_user(form.id.data)
        user.set_password(form.password.data)

        db.session.commit()

        return redirect('/users')
    
    return render_template('pwresetuser.html', user=user, form=form, edit_request=edit_request)