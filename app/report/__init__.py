from flask import Blueprint

bp = Blueprint('report', __name__, url_prefix='/report', template_folder='templates')

from app.report import routes