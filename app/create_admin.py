from app import app, models
from flask import Flask
app = Flask(__name__)
from app.models import User, Role, db
import uuid

def create_admin():

    if User.query.filter_by(id=1).first() == None:
        admin = models.User(id=1, username='admin', roles=[Role.query.filter_by(id=1).first()], fname='Admin', lname='Admin', fs_uniquifier=uuid.uuid4().hex, active=True)
        admin.set_password("admin")

    try:
        db.session.add(admin)
        db.session.commit()
        print("Admin Created")
    except:
        print("Admin Already Initialized")