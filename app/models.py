from datetime import datetime, timezone, date, timedelta
from typing import Optional
from flask_login import UserMixin
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

    role: so.Mapped[str] = so.mapped_column(sa.String(64))

    roles = db.relationship('Role', secondary='user_roles')

    fname: so.Mapped[str] = so.mapped_column(sa.String(64))

    lname: so.Mapped[str] = so.mapped_column(sa.String(64))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#Role Data Model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    
#UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Registrations(db.Model):
    regid: so.Mapped[int] = so.mapped_column(primary_key=True)
    order_id: so.Mapped[Optional[int]]
    fname: so.Mapped[str] 
    lname: so.Mapped[str] 
    scaname: so.Mapped[Optional[str]] 
    kingdom: so.Mapped[Optional[str]] 
    event_ticket: so.Mapped[Optional[str]] 
    rate_mbr: so.Mapped[Optional[str]] 
    rate_age: so.Mapped[Optional[str]] 
    rate_date: so.Mapped[Optional[str]] 
    price_calc: so.Mapped[Optional[int]]
    price_paid: so.Mapped[Optional[int]]
    price_due: so.Mapped[Optional[int]]
    lodging: so.Mapped[Optional[str]] 
    pay_type: so.Mapped[Optional[str]]
    prereg_status: so.Mapped[Optional[str]] 
    mbr_num_exp: so.Mapped[Optional[str]] 
    mbr_num: so.Mapped[Optional[int]]
    mbr_exp: so.Mapped[Optional[date]]
    requests: so.Mapped[Optional[str]] 
    checkin: so.Mapped[Optional[datetime]]
    medallion: so.Mapped[Optional[int]]
    signature: so.Mapped[Optional[str]]
    reg_date_time: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now().replace(microsecond=0).isoformat())

    def __repr__(self):
        return '<Registrations {}>'.format(self.regid)