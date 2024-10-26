from app import app, models
from flask import Flask
app = Flask(__name__)
from app.models import Role, db

def create_roles():
    if Role.query.filter_by(id=1) is None:
        admin = models.Role(id=1, name="Admin")
        db.session.add(admin)

    roles = Role.query.all()

    role_array = []
    for role in roles:
        role_array.append(role.name)

    if "Troll Shift Lead" not in role_array:
        troll_shift_lead = Role(id=2, name="Troll Shift Lead")
        db.session.add(troll_shift_lead)
    if "Troll User" not in role_array:
        troll_user = Role(id=3, name="Troll User")
        db.session.add(troll_user)
    if "Marshal Admin" not in role_array:
        marshal_admin = Role(id=4, name="Marshal Admin")
        db.session.add(marshal_admin)
    if "Marshal User" not in role_array:
        marshal_user = Role(id=5, name="Marshal User")
        db.session.add(marshal_user)
    if "Land" not in role_array:
        land = Role(id=6, name="Land")
        db.session.add(land)
    if "Invoices" not in role_array:
        invoices = Role(id=7, name="Invoices")
        db.session.add(invoices)
    if "Cashier" not in role_array:
        cashiers = Role(id=8, name="Cashier")
        db.session.add(cashiers)

    db.session.commit()

    print("Roles Created")