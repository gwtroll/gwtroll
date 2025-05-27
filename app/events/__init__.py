from flask import Blueprint

bp = Blueprint('events', __name__, url_prefix='/events', template_folder='templates')

from app.events import routes