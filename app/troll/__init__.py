from flask import Blueprint

bp = Blueprint('troll', __name__, url_prefix='/troll', template_folder='templates')

from app.troll import routes