from flask import Blueprint

bp = Blueprint('scheduledevents', __name__, url_prefix='/scheduledevents', template_folder='templates')

from app.scheduledevents import routes