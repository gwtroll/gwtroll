from flask import Blueprint

bp = Blueprint('lodging', __name__, url_prefix='/lodging', template_folder='templates')

from app.lodging import routes