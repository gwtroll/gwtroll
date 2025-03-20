from flask import Blueprint

bp = Blueprint('marshal', __name__, url_prefix='/marshal', template_folder='templates')

from app.marshal import routes