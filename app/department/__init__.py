from flask import Blueprint

bp = Blueprint('department', __name__, url_prefix='/department', template_folder='templates')

from app.department import routes