from datetime import datetime
from typing import Optional
from flask_security import UserMixin, RoleMixin, UserMixin
import sqlalchemy as sa
from sqlalchemy import Computed
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    
    #email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
    #                                        unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    roles = db.relationship('Role', secondary='user_roles')

    fname: so.Mapped[str] = so.mapped_column(sa.String(64))

    lname: so.Mapped[str] = so.mapped_column(sa.String(64))

    medallion = db.Column(db.Integer())

    active = db.Column(db.Boolean())

    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship("Event", backref='users')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if password == '': 
            if self.password_hash == None:
                return True
        else:
            return check_password_hash(self.password_hash, password)


#Role Data Model
class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    def __repr__(self):
        return '<Role {}>'.format(self.name)
    
#UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

@login.user_loader
def load_user(id):
    return User.query.filter_by(fs_uniquifier=id).first()

class Registrations(db.Model):
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    #Basic
    fname = db.Column(db.String())
    lname = db.Column(db.String())
    scaname = db.Column(db.String())
    city = db.Column(db.String())
    state_province = db.Column(db.String())
    zip = db.Column(db.Integer())
    country = db.Column(db.String())
    phone = db.Column(db.String())
    email = db.Column(db.String())
    invoice_email = db.Column(db.String())
    age = db.Column(db.String())
    emergency_contact_name = db.Column(db.String())
    emergency_contact_phone = db.Column(db.String())
    royal_departure_date = db.Column(db.Date())
    royal_title = db.Column(db.String())

    #Membership
    mbr = db.Column(db.Boolean(), default=False)
    mbr_num_exp = db.Column(db.String())
    mbr_num = db.Column(db.Integer())
    
    #Prereg/Reg
    reg_date_time = db.Column(db.DateTime(), default=lambda: datetime.now().replace(microsecond=0).isoformat())
    prereg = db.Column(db.Boolean(), default=False)
    prereg_date_time = db.Column(db.DateTime())
    expected_arrival_date = db.Column(db.Date())
    early_on = db.Column(db.String())
    notes = db.Column(db.Text)
    duplicate = db.Column(db.Boolean, default=False)
    
    #Pricing
    registration_price = db.Column(db.Integer(), default=0)
    registration_balance = db.Column(db.Integer(), default=0)
    nmr_price = db.Column(db.Integer(), default=0)
    nmr_balance = db.Column(db.Integer(), default=0)
    paypal_donation = db.Column(db.Integer(), default=0)
    paypal_donation_balance = db.Column(db.Integer(), default=0)
    nmr_donation = db.Column(db.Integer(), default=0)
    total_due = db.Column(db.Integer(), Computed(registration_price+nmr_price+paypal_donation))
    balance = db.Column(db.Integer(), default=0)

    #Troll
    minor_waiver = db.Column(db.String())
    checkin = db.Column(db.DateTime())
    medallion = db.Column(db.Integer())
    signature = db.Column(db.String())
    actual_arrival_date = db.Column(db.Date())
    
    #Relationships
    invoice_number = db.Column(db.Integer(), db.ForeignKey('invoice.invoice_number'))
    invoice = db.relationship("Invoice", back_populates="regs")
    payments = db.relationship("Payment", back_populates="reg")
    bows = db.relationship('Bows', secondary='reg_bows')
    crossbows = db.relationship('Crossbows', secondary='reg_crossbows')
    marshal_inspections = db.relationship('MarshalInspection', backref='registrations')
    incident_report = db.relationship('IncidentReport', backref='registrations')
    kingdom_id = db.Column(db.Integer(), db.ForeignKey('kingdom.id'))
    kingdom = db.relationship("Kingdom", backref="regs")
    lodging_id = db.Column(db.Integer(), db.ForeignKey('lodging.id'))
    lodging = db.relationship("Lodging", backref="regs")

    #Event
    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship("Event", backref='registrations')

    def __repr__(self):
        return '<Registrations {}>'.format(self.id)
    
    def toJSON(self):
        data_dict = {}
        print(self.__dict__)
        for key in self.__dict__:
            if not key.startswith("_"):
                if isinstance(self.__dict__[key], datetime):
                    data_dict[key] = datetime.strftime(self.__dict__[key],'%Y-%m-%d')
                else:
                    print(self.__dict__[key])
                    data_dict[key] = self.__dict__[key]
        return json.dumps(data_dict)
    
class Invoice(db.Model):
    __tablename__ = 'invoice'
    invoice_number = db.Column(db.Integer(), primary_key=True)
    invoice_email = db.Column(db.String(),nullable=False)
    invoice_date = db.Column(db.DateTime(),nullable=False)
    invoice_status = db.Column(db.String(),nullable=False)
    registration_total = db.Column(db.Integer(), default=0)
    nmr_total = db.Column(db.Integer(), default=0)
    donation_total = db.Column(db.Integer(), default=0)
    invoice_total = db.Column(db.Integer(), Computed(registration_total+nmr_total+donation_total))
    balance = db.Column(db.Integer())
    notes = db.Column(db.Text())
    regs = db.relationship("Registrations", back_populates="invoice")
    payments = db.relationship("Payment", back_populates="invoice")
    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship("Event", backref='invoice')


class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.String(), nullable=False)
    check_num = db.Column(db.Integer())
    payment_date = db.Column(db.DateTime(), nullable=False)
    registration_amount = db.Column(db.Integer(), default=0)
    nmr_amount = db.Column(db.Integer(), default=0)
    paypal_donation_amount = db.Column(db.Integer(), default=0)
    amount = db.Column(db.Integer(), nullable=False)
    invoice_number  = db.Column(db.Integer(), db.ForeignKey('invoice.invoice_number'))
    invoice = db.relationship("Invoice", back_populates="payments")
    reg_id  = db.Column(db.Integer(), db.ForeignKey('registrations.id'))
    reg = db.relationship("Registrations", back_populates="payments")
    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship("Event", backref='payment')
    
class RegLogs(db.Model):
    __tablename__ = 'reglogs'  
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer(), db.ForeignKey('registrations.id'))
    userid = db.Column(db.Integer(), db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime())
    action = db.Column(db.String())
    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship("Event", backref='reglogs')

class MarshalInspection(db.Model):
    __tablename__ = 'marshal_inspection' 
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer, db.ForeignKey('registrations.id'))
    inspection_type = db.Column(db.String())
    inspection_date = db.Column(db.DateTime())
    inspecting_marshal_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    inspecting_marshal = db.relationship('User', foreign_keys=[inspecting_marshal_id])
    inspected = db.Column(db.Boolean())

class Bows(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    poundage = db.Column(db.Double())
    bow_inspection_date: so.Mapped[Optional[datetime]]
    bow_inspection_marshal_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    bow_inspection_marshal = db.relationship('User', foreign_keys=[bow_inspection_marshal_id])

    def __repr__(self):
        return '<Bow {}>'.format(self.id)
    
class RegBows(db.Model):
    __tablename__ = 'reg_bows'
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer(), db.ForeignKey('registrations.id', ondelete='CASCADE'))
    bowid = db.Column(db.Integer(), db.ForeignKey('bows.id', ondelete='CASCADE'))
    
class Crossbows(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    inchpounds = db.Column(db.Double())
    crossbow_inspection_date: so.Mapped[Optional[datetime]]
    crossbow_inspection_marshal_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    crossbow_inspection_marshal = db.relationship('User', foreign_keys=[crossbow_inspection_marshal_id])

    def __repr__(self):
        return '<CrossBow {}>'.format(self.id)
    
class RegCrossBows(db.Model):
    __tablename__ = 'reg_crossbows'
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer(), db.ForeignKey('registrations.id', ondelete='CASCADE'))
    crossbowid = db.Column(db.Integer(), db.ForeignKey('crossbows.id', ondelete='CASCADE'))

class IncidentReport(db.Model):
    __tablename__ = 'incidentreport'
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer, db.ForeignKey('registrations.id'))
    report_date = db.Column(db.DateTime())
    incident_date = db.Column(db.DateTime())
    reporting_user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    reporting_user = db.relationship('User', foreign_keys=[reporting_user_id])
    notes = db.Column(db.Text())
    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship("Event", backref='incidentreport')

class PriceSheet(db.Model):
    __tablename__ = 'pricesheet'
    arrival_date = db.Column(db.Date(), primary_key=True)
    prereg_price = db.Column(db.Integer())
    atd_price = db.Column(db.Integer())
    nmr = db.Column(db.Integer())
    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship("Event", backref='pricesheet')

class Kingdom(db.Model):
    __tablename__ = 'kingdom'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)

class Lodging(db.Model):
    __tablename__ = 'lodging'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship("Event", backref='lodging')

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    start_date = db.Column(db.Date(), nullable=False)
    end_date = db.Column(db.Date(), nullable=False)
    location = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text(), nullable=False)