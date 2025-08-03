from flask import render_template
from app.user import bp

from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, url_for, flash, redirect
from app.forms import *
from app.models import *

@bp.route('/myaccount', methods=['GET', 'POST'])
@login_required
def myaccount():
    return render_template('myaccount.html', acc=current_user, checkedincount=reg_count())

@bp.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = UpdatePasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_object(current_user)
        db.session.commit()
        flash("Password Successfully Changed!")
        return redirect(url_for('user.myaccount'))
    else:
        return render_template('changepassword.html', form=form, user=current_user)