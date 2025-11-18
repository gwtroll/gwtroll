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
from app.utils.email_utils import send_new_user_email
import random
import string

def generate_temp_password(length):
    """Generates a temporary password of a specified length."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.sample(characters, length))
    return password

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
        user.set_password(form.password.data.strip())
        db.session.commit()
        return redirect(url_for('users.users'))
    
    return render_template('pwresetuser.html', user=user, form=form)

@bp.route('/upload', methods=('GET', 'POST'))
@login_required
@permission_required('admin')
def uploadusers():
    form = StandardUploadForm()
    if request.method == 'POST':
        file = request.files['file']
        try:
            for line in file.stream:
                print(line)
                line_content = line.decode('utf-8').strip()
                new_row = line_content.split(',')
                department_string = new_row[0].strip()
                department = get_department_by_name(department_string)
                email = new_row[1].strip().lower()
                fname = new_row[2].strip()
                lname = new_row[3].strip()
                username = new_row[4].strip().lower()
                role_string = new_row[5].strip()
                role = get_role_by_name(role_string)
                
                new_user = User(
                    username=username,
                    department_id=department.id,
                    email=email,
                    fname=fname,
                    lname=lname,
                    medallion=0,
                    active=True
                )
                new_user.roles.append(role)
                new_user.fs_uniquifier = uuid.uuid4().hex
                password = generate_temp_password(8)
                new_user.set_password(password)
                db.session.add(new_user)
                if new_user.email != None:
                    send_new_user_email(email, fname, lname, username, password)
        finally:
            db.session.commit()

            return redirect(url_for('users.users'))

    return render_template('uploadusers.html', form=form)