from flask import render_template
from app.report import bp
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
def reports():

    return render_template("viewreport.html")
