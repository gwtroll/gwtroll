from flask import Blueprint

bp = Blueprint('registration', __name__, url_prefix='/registration', template_folder='templates')

from app.registration import routes