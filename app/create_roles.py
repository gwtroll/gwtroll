from app import app, models
from flask import Flask
app = Flask(__name__)
from app.models import Role, db

def create_roles():
    if Role.query.filter_by(id=1) is None:
        admin = models.Role(id=1, name="Admin")
        troll_shift_lead = Role(id=2, name="Troll Shift Lead")
        troll_user = Role(id=3, name="Troll User")
        marshal_admin = Role(id=4, name="Marshal Admin")
        marshal_user = Role(id=5, name="Marshal User")
        land = Role(id=6, name="Land")
        

        db.session.add(admin)
        db.session.add(troll_shift_lead)
        db.session.add(troll_user)
        db.session.add(marshal_admin)
        db.session.add(marshal_user)
        db.session.add(land)
        db.session.commit()

        print("Roles Created")