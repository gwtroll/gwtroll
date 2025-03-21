from flask import render_template
from app.user import bp

from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, url_for, flash, redirect
from app.forms import *
from app.models import *

@bp.route('/myaccount', methods=['GET', 'POST'])
@login_required
def myaccount():
    checkedincount = len(RegLogs.query.filter(RegLogs.userid == current_user.id, RegLogs.action == 'CHECKIN').all())
    return render_template('myaccount.html', acc=current_user, checkedincount=checkedincount)

@bp.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = UpdatePasswordForm()
    form.id.data = current_user.id
    form.username.data = current_user.username
    if request.method == 'POST' and form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash("Password Successfully Changed!")
        return redirect(url_for('user.myaccount'))
    elif request.method == 'POST' and not form.validate_on_submit():
        for field in form.errors:
            flash(form.errors[field],'error')
        return render_template('changepassword.html', form=form, user=current_user)
    else:
        return render_template('changepassword.html', form=form, user=current_user)