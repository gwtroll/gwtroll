from flask import render_template
from app.department import bp

from flask_login import login_required
from flask import render_template, request, redirect, url_for
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted

@bp.route('/', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def department():
    all_department = Department.query.order_by(Department.name).all()
    print(all_department)
    return render_template('viewdepartment.html', departments=all_department)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def createdepartment():
    form = DepartmentForm()
    if request.method == 'POST':
        department = Department(
            name=request.form.get('name'),
            description=request.form.get('description'),
        )
        db.session.add(department)
        db.session.commit()
        return redirect(url_for('department.department'))
    return render_template('createdepartment.html', form=form)

@bp.route('/<departmentid>', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def editdepartment(departmentid):
    department = Department.query.get(departmentid)
    form = DepartmentForm(
        name=department.name,
        description=department.description
    )
    form.submit.label.text = 'Update Department'
    if request.method == 'POST':
        department.name = request.form.get('name')
        db.session.commit()
        return redirect(url_for('department.department'))
    return render_template('editdepartment.html', form=form, department=department)

@bp.route('/<departmentid>/delete', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def deletedepartment(departmentid):
    department = Department.query.get(departmentid)

    if request.method == 'POST':
        db.session.delete(department)
        db.session.commit()
        return redirect(url_for('department.department'))
    return render_template('deletedepartment.html', department=department)