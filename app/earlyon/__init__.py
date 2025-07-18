from flask import Blueprint

bp = Blueprint('earlyon', __name__, url_prefix='/earlyon', template_folder='templates')

from app.earlyon import routes