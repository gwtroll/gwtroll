from flask import Blueprint

bp = Blueprint('roles', __name__, url_prefix='/roles', template_folder='templates')

from app.roles import routes