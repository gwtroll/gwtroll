from datetime import datetime, timezone, date, timedelta
from typing import Optional
from flask_security import SQLAlchemyUserDatastore, UserMixin, RoleMixin, UserMixin, login_required
from flask_login import LoginManager
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash

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

    active = db.Column(db.Boolean())

    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)

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
    regid: so.Mapped[int] = so.mapped_column(primary_key=True)
    order_id: so.Mapped[Optional[int]]
    invoice_number: so.Mapped[Optional[str]] 
    invoice_paid: so.Mapped[bool] = so.mapped_column(default=False)
    invoice_date: so.Mapped[Optional[datetime]]
    invoice_payment_date: so.Mapped[Optional[datetime]]
    invoice_canceled: so.Mapped[bool] = so.mapped_column(default=False)
    invoice_status: so.Mapped[Optional[str]]
    refund_check_num: so.Mapped[Optional[int]]
    fname: so.Mapped[str] 
    lname: so.Mapped[str] 
    scaname: so.Mapped[Optional[str]] 
    city: so.Mapped[Optional[str]] 
    state_province: so.Mapped[Optional[str]] 
    zip: so.Mapped[Optional[int]] 
    country: so.Mapped[Optional[str]] 
    phone: so.Mapped[Optional[str]] 
    email: so.Mapped[Optional[str]]
    invoice_email: so.Mapped[Optional[str]]
    kingdom: so.Mapped[Optional[str]] 
    event_ticket: so.Mapped[Optional[str]] 
    rate_mbr: so.Mapped[Optional[str]] 
    rate_age: so.Mapped[Optional[str]] 
    rate_date: so.Mapped[Optional[str]] 
    price_calc: so.Mapped[Optional[int]]
    price_paid: so.Mapped[Optional[int]]
    atd_paid: so.Mapped[Optional[int]]
    atd_pay_type: so.Mapped[Optional[str]]
    price_due: so.Mapped[Optional[int]]
    paypal_donation: so.Mapped[Optional[bool]] = so.mapped_column(default=False)
    paypal_donation_amount: so.Mapped[Optional[int]] = so.mapped_column(default=0)
    lodging: so.Mapped[Optional[str]] 
    pay_type: so.Mapped[Optional[str]]
    prereg_status: so.Mapped[Optional[str]]
    early_on: so.Mapped[Optional[bool]]
    mbr_num_exp: so.Mapped[Optional[str]] 
    mbr_num: so.Mapped[Optional[int]]
    onsite_contact_name: so.Mapped[Optional[str]] 
    onsite_contact_sca_name: so.Mapped[Optional[str]] 
    onsite_contact_kingdom: so.Mapped[Optional[str]] 
    onsite_contact_group: so.Mapped[Optional[str]] 
    offsite_contact_name: so.Mapped[Optional[str]] 
    offsite_contact_phone: so.Mapped[Optional[str]] 
    # UNCOMMENT ONCE DB UPDATED - MINOR WAIVER STATUS
    # minor_waiver: so.Mapped[Optional[str]] 
    requests: so.Mapped[Optional[str]] 
    checkin: so.Mapped[Optional[datetime]]
    medallion: so.Mapped[Optional[int]]
    signature: so.Mapped[Optional[str]]
    prereg_date_time: so.Mapped[Optional[datetime]]
    royal_departure_date: so.Mapped[Optional[datetime]]
    royal_title: so.Mapped[Optional[str]]
    reg_date_time: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now().replace(microsecond=0).isoformat())
    bows = db.relationship('Bows', secondary='reg_bows')
    crossbows = db.relationship('Crossbows', secondary='reg_crossbows')
    martial_inspections = db.relationship('MartialInspection', backref='registrations')
    incident_report = db.relationship('IncidentReport', backref='registrations')

    def __repr__(self):
        return '<Registrations {}>'.format(self.regid)
    
class RegLogs(db.Model):
    __tablename__ = 'reglogs'  
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer(), db.ForeignKey('registrations.regid'))
    userid = db.Column(db.Integer(), db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime())
    action = db.Column(db.String())

class MartialInspection(db.Model):
    __tablename__ = 'martial_inspection' 
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer, db.ForeignKey('registrations.regid'))
    inspection_type = db.Column(db.String())
    inspection_date = db.Column(db.DateTime())
    inspecting_martial_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    inspecting_martial = db.relationship('User', foreign_keys=[inspecting_martial_id])
    inspected = db.Column(db.Boolean())

class Bows(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    poundage = db.Column(db.Double())
    bow_inspection_date: so.Mapped[Optional[datetime]]
    bow_inspection_martial_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    bow_inspection_martial = db.relationship('User', foreign_keys=[bow_inspection_martial_id])

    def __repr__(self):
        return '<Bow {}>'.format(self.id)
    
class RegBows(db.Model):
    __tablename__ = 'reg_bows'
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer(), db.ForeignKey('registrations.regid', ondelete='CASCADE'))
    bowid = db.Column(db.Integer(), db.ForeignKey('bows.id', ondelete='CASCADE'))
    
class Crossbows(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    inchpounds = db.Column(db.Double())
    crossbow_inspection_date: so.Mapped[Optional[datetime]]
    crossbow_inspection_martial_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    crossbow_inspection_martial = db.relationship('User', foreign_keys=[crossbow_inspection_martial_id])

    def __repr__(self):
        return '<CrossBow {}>'.format(self.id)
    
class RegCrossBows(db.Model):
    __tablename__ = 'reg_crossbows'
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer(), db.ForeignKey('registrations.regid', ondelete='CASCADE'))
    crossbowid = db.Column(db.Integer(), db.ForeignKey('crossbows.id', ondelete='CASCADE'))

class IncidentReport(db.Model):
    __tablename__ = 'incidentreport'
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer, db.ForeignKey('registrations.regid'))
    report_date = db.Column(db.DateTime())
    incident_date = db.Column(db.DateTime())
    reporting_user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    reporting_user = db.relationship('User', foreign_keys=[reporting_user_id])
    notes = db.Column(db.Text())