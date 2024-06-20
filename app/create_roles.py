from app import app, models
from flask import Flask
app = Flask(__name__)
from app.models import Role, db

def create_roles():
    if Role.query.filter_by(id=1) is None:
        admin = models.Role(id=1, name="Admin")
        shift_lead = Role(id=2, name="Shift Lead")
        marshal = Role(id=3, name="Marshal")
        land = Role(id=4, name="Land")
        user = Role(id=5, name="User")

        db.session.add(admin)
        db.session.add(shift_lead)
        db.session.add(marshal)
        db.session.add(land)
        db.session.add(user)
        db.session.commit()

        print("Roles Created")