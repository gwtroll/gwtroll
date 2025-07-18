
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from flask_security.models import fsqla_v3 as fsqla
from flask_mail import Mail
from flask_qrcode import QRcode

app = Flask(__name__,static_url_path="", static_folder="static")

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
qrcode = QRcode(app)

mail = Mail(app)

from app import routes, models
from app.models import Role, User

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore)

from app.user import bp as user_bp
from app.users import bp as users_bp
from app.invoices import bp as invoices_bp
from app.marshal import bp as marshal_bp
from app.registration import bp as registration_bp
from app.earlyon import bp as earlyon_bp
from app.troll import bp as troll_bp
from app.roles import bp as roles_bp
# from app.events import bp as events_bp
from app.eventvariables import bp as eventvariables_bp 
from app.lodging import bp as lodging_bp
from app.kingdom import bp as kingdom_bp
from app.department import bp as department_bp
from app.merchant import bp as merchant_bp
app.register_blueprint(user_bp)
app.register_blueprint(users_bp)
app.register_blueprint(invoices_bp)
app.register_blueprint(marshal_bp)
app.register_blueprint(registration_bp)
app.register_blueprint(earlyon_bp)
app.register_blueprint(troll_bp)
app.register_blueprint(roles_bp)
# app.register_blueprint(events_bp)
app.register_blueprint(eventvariables_bp)
app.register_blueprint(lodging_bp)
app.register_blueprint(kingdom_bp)
app.register_blueprint(department_bp)
app.register_blueprint(merchant_bp)