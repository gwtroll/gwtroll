from flask import Blueprint

bp = Blueprint('eventvariables', __name__, url_prefix='/eventvariables', template_folder='templates')

from app.eventvariables import routes