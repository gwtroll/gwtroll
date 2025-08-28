from flask import Blueprint

bp = Blueprint('recruitment', __name__, url_prefix='/recruitment', template_folder='templates')

from app.recruitment import routes