from flask import Blueprint

bp = Blueprint('kingdom', __name__, url_prefix='/kingdom', template_folder='templates')

from app.kingdom import routes