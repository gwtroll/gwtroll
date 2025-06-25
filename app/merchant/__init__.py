from flask import Blueprint

bp = Blueprint('merchant', __name__, url_prefix='/merchant', template_folder='templates')

from app.merchant import routes