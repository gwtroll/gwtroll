from flask import Blueprint

bp = Blueprint('payment', __name__, url_prefix='/payment', template_folder='templates')

from app.payment import routes