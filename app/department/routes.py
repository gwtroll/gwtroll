from flask import render_template
from app.department import bp
from app.utils.security_utils import *
from flask_login import login_required
from flask import render_template, request, redirect, url_for
from app.forms import *
from app.models import *
from app.utils.db_utils import *

from flask_security import roles_accepted


@bp.route("/", methods=("GET", "POST"))
@login_required
@permission_required("admin")
def department():
    all_department = Department.query.order_by(Department.name).all()
    db.session.close()
    return render_template("viewdepartment.html", departments=all_department)


@bp.route("/create", methods=("GET", "POST"))
@login_required
@permission_required("admin")
def createdepartment():
    form = DepartmentForm()
    if request.method == "POST":
        department = Department(
            name=request.form.get("name"),
            description=request.form.get("description"),
        )
        db.session.add(department)
        db.session.commit()
        db.session.close()
        return redirect(url_for("department.department"))
    db.session.close()
    return render_template("createdepartment.html", form=form)


@bp.route("/<departmentid>", methods=("GET", "POST"))
@login_required
@permission_required("admin")
def editdepartment(departmentid):
    department = Department.query.get(departmentid)
    form = DepartmentForm(name=department.name, description=department.description)
    form.submit.label.text = "Update Department"
    if request.method == "POST":
        department.name = request.form.get("name")
        db.session.commit()
        db.session.close()
        return redirect(url_for("department.department"))
    db.session.close()
    return render_template("editdepartment.html", form=form, department=department)


@bp.route("/<departmentid>/delete", methods=("GET", "POST"))
@login_required
@permission_required("admin")
def deletedepartment(departmentid):
    department = Department.query.get(departmentid)
    if request.method == "POST":
        db.session.delete(department)
        db.session.commit()
        db.session.close()
        return redirect(url_for("department.department"))
    db.session.close()
    return render_template("deletedepartment.html", department=department)
