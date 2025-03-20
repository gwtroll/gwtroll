from flask import Blueprint

bp = Blueprint('invoices', __name__, url_prefix='/invoices', template_folder='templates')

from app.invoices import routes