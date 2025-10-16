from datetime import datetime
import pytz
from typing import Optional
from flask_security import UserMixin, RoleMixin, UserMixin
import sqlalchemy as sa
from sqlalchemy import Computed
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
import json


class EventVariables(db.Model):
    __tablename__ = "eventvariables"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    event_title = db.Column(db.String(), nullable=False)
    start_date = db.Column(db.Date(), nullable=False)
    end_date = db.Column(db.Date(), nullable=False)
    location = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    preregistration_open_date = db.Column(db.Date(), nullable=False)
    preregistration_close_date = db.Column(db.Date(), nullable=False)
    autocrat1 = db.Column(db.String(), nullable=True)
    autocrat2 = db.Column(db.String(), nullable=True)
    autocrat3 = db.Column(db.String(), nullable=True)
    reservationist = db.Column(db.String(), nullable=True)
    merchant_application_deadline = db.Column(db.Date(), nullable=False)
    merchantcrat_email = db.Column(db.String(), nullable=False)
    marchantcrat_phone = db.Column(db.String(), nullable=False)
    merchant_preregistration_open_date = db.Column(db.Date(), nullable=False)
    merchant_preregistration_close_date = db.Column(db.Date(), nullable=False)
    merchant_processing_fee = db.Column(db.Integer(), default=20, nullable=False)
    merchant_late_processing_fee = db.Column(db.Integer(), default=45, nullable=False)
    merchant_squarefoot_fee = db.Column(db.Numeric(10, 2), default=0.10, nullable=False)
    merchant_bounced_check_fee = db.Column(db.Integer(), default=35, nullable=False)
    # bas = db.Column(db.String(), nullable=True)
    # cli = db.Column(db.String(), nullable=True)
    # sec = db.Column(db.String(), nullable=True)
    # web = db.Column(db.String(), nullable=True)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), nullable=True)

    # email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
    #                                        unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    roles = db.relationship("Role", secondary="user_roles")

    fname: so.Mapped[str] = so.mapped_column(sa.String(64))

    lname: so.Mapped[str] = so.mapped_column(sa.String(64))

    medallion = db.Column(db.Integer())

    department_id = db.Column(db.Integer(), db.ForeignKey("departments.id"))
    department = db.relationship("Department", backref="user_department", viewonly=True)

    scheduled_events = db.relationship(
        "ScheduledEvent", secondary="user_scheduledevents"
    )

    active = db.Column(db.Boolean())

    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)

    # event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    # event = db.relationship("Event", backref='users')

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if password == "":
            if self.password_hash == None:
                return True
        else:
            return check_password_hash(self.password_hash, password)

    def get_permission_set(self):
        permission_set = []
        for role in self.roles:
            for permission in role.permissions:
                if permission.name not in permission_set:
                    permission_set.append(permission.name)
        return permission_set

    def has_permission(self, query_permission):
        for role in self.roles:
            for permission in role.permissions:
                if query_permission == permission.name or permission.name == "admin":
                    return True
        return False

    def get_scheduledevent_ids(self):
        return [event.id for event in self.scheduled_events]


# Role Data Model
class Role(db.Model, RoleMixin):
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    permissions = db.relationship("Permissions", secondary="role_permissions")

    def __repr__(self):
        return "<Role {}>".format(self.name)


# UserRoles association table
class UserRoles(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE"))


class Permissions(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


class RolePermissions(db.Model):
    __tablename__ = "role_permissions"
    id = db.Column(db.Integer(), primary_key=True)
    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE"))
    permission_id = db.Column(
        db.Integer(), db.ForeignKey("permissions.id", ondelete="CASCADE")
    )


@login.user_loader
def load_user(id):
    return User.query.filter_by(fs_uniquifier=id).first()


class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=True)
    users = db.relationship("User", backref="department_user", lazy=True)

    def __repr__(self):
        return "<Department {}>".format(self.name)


class EarlyOnRequest(db.Model):
    __tablename__ = "earlyonrequest"
    id = db.Column(db.Integer(), primary_key=True)
    arrival_date = db.Column(db.Date(), nullable=False)
    reg_id = db.Column(db.Integer(), db.ForeignKey("registrations.id"))
    registration = db.relationship("Registrations", backref="earlyonrequest")
    department_id = db.Column(db.Integer(), db.ForeignKey("departments.id"))
    department = db.relationship("Department", backref="earlyonrequest")
    request_date = db.Column(
        db.DateTime(),
        default=lambda: datetime.now(pytz.timezone("America/Chicago")).replace(
            microsecond=0
        ),
    )
    earlyonriders = db.relationship("EarlyOnRider", secondary="earlyonrequest_riders")
    dept_approval_status = db.Column(db.String(), default="PENDING")
    autocrat_approval_status = db.Column(db.String(), default="PENDING")
    rider_cost = db.Column(db.Integer(), default=0)
    rider_balance = db.Column(db.Integer(), default=0)
    invoice_number = db.Column(db.Integer(), db.ForeignKey("invoice.invoice_number"))
    invoice = db.relationship("Invoice", back_populates="earlyonrequests")
    payments = db.relationship("Payment", back_populates="earlyonrequest")
    notes = db.Column(db.Text())

    def recalculate_balance(self):
        balance = self.rider_cost
        rider_balance = self.rider_cost
        for payment in self.payments:
            balance -= payment.amount
            rider_balance -= payment.rider_fee_amount
        if balance < 0:
            balance = 0
        self.balance = balance
        if rider_balance < 0:
            rider_balance = 0
        self.rider_balance = rider_balance
    
    def get_invoice_items(self):
        items = []
        if self.rider_balance > 0:
            items.append({
                'name':'Extra Riders Fee',
                'description':'Gulf Wars Early On Extra Riders Fee',
                'quantity':'1',
                'unit_amount':{
                    'currency_code':'USD',
                    'value':str(self.rider_balance)
                },
                'unit_of_measure': 'QUANTITY'
            })
        return items


class EarlyOnRider(db.Model):
    __tablename__ = "earlyonrider"
    id = db.Column(db.Integer(), primary_key=True)
    fname = db.Column(db.String(), nullable=False)
    lname = db.Column(db.String(), nullable=False)
    scaname = db.Column(db.String(), nullable=False)
    minor = db.Column(db.Boolean(), default=False)
    regid = db.Column(
        db.Integer(), db.ForeignKey("registrations.id", ondelete="CASCADE")
    )
    reg = db.relationship("Registrations", backref="earlyonriders")


class EarlyOnRequestRiders(db.Model):
    __tablename__ = "earlyonrequest_riders"
    id = db.Column(db.Integer(), primary_key=True)
    earlyonrequest_id = db.Column(
        db.Integer(), db.ForeignKey("earlyonrequest.id", ondelete="CASCADE")
    )
    earlyonrider_id = db.Column(
        db.Integer(), db.ForeignKey("earlyonrider.id", ondelete="CASCADE")
    )
    earlyonrequest = db.relationship(
        "EarlyOnRequest", backref="earlyonrequest_riders", viewonly=True
    )
    earlyonrider = db.relationship(
        "EarlyOnRider", backref="earlyonrequest_riders", viewonly=True
    )


class Registrations(db.Model):
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    # Basic
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

    # Membership
    mbr = db.Column(db.Boolean(), default=False)
    mbr_num_exp = db.Column(db.Date())
    mbr_num = db.Column(db.Integer())

    # Prereg/Reg
    reg_date_time = db.Column(
        db.DateTime(),
        default=lambda: datetime.now(pytz.timezone("America/Chicago"))
        .replace(microsecond=0)
        .isoformat(),
    )
    prereg = db.Column(db.Boolean(), default=False)
    expected_arrival_date = db.Column(db.Date())
    early_on_approved = db.Column(db.Boolean(), default=False)
    notes = db.Column(db.Text)
    duplicate = db.Column(db.Boolean, default=False)
    canceled = db.Column(db.Boolean, default=False) 

    # Pricing
    registration_price = db.Column(db.Integer(), default=0)
    registration_balance = db.Column(db.Integer(), default=0)
    nmr_price = db.Column(db.Integer(), default=0)
    nmr_balance = db.Column(db.Integer(), default=0)
    paypal_donation = db.Column(db.Integer(), default=0)
    paypal_donation_balance = db.Column(db.Integer(), default=0)
    nmr_donation = db.Column(db.Integer(), default=0)
    total_due = db.Column(
        db.Integer(), Computed(registration_price + nmr_price + paypal_donation)
    )
    balance = db.Column(db.Integer(), default=0)

    # Troll
    minor_waiver = db.Column(db.String())
    checkin = db.Column(db.DateTime())
    medallion = db.Column(db.Integer())
    signature = db.Column(db.String())
    actual_arrival_date = db.Column(db.Date())

    # Relationships
    invoice_number = db.Column(db.Integer(), db.ForeignKey("invoice.invoice_number"))
    invoice = db.relationship("Invoice", backref="inv_regs")
    payments = db.relationship("Payment", back_populates="reg")
    bows = db.relationship("Bows", secondary="reg_bows")
    crossbows = db.relationship("Crossbows", secondary="reg_crossbows")
    marshal_inspections = db.relationship("MarshalInspection", backref="registrations")
    incident_report = db.relationship("IncidentReport", backref="registrations")
    kingdom_id = db.Column(db.Integer(), db.ForeignKey("kingdom.id"))
    kingdom = db.relationship("Kingdom", backref="regs")
    lodging_id = db.Column(db.Integer(), db.ForeignKey("lodging.id"))
    lodging = db.relationship("Lodging", backref="regs")
    earlyonrequests_ref = db.relationship("EarlyOnRequest", back_populates="registration", viewonly=True)
    earlyonriders_ref = db.relationship("EarlyOnRider", back_populates="reg", viewonly=True)

    # Event
    # event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    # event = db.relationship("Event", backref='registrations')

    def __repr__(self):
        return "<Registrations {}>".format(self.id)

    def toJSON(self):
        data_dict = {}
        for key in self.__dict__:
            if not key.startswith("_"):
                if isinstance(self.__dict__[key], datetime):
                    data_dict[key] = datetime.strftime(self.__dict__[key], "%Y-%m-%d")
                else:
                    data_dict[key] = self.__dict__[key]
        return json.dumps(data_dict, sort_keys=True, default=str)

    def recalculate_balance(self):
        balance = (
            self.registration_price
            + self.nmr_price
            + self.paypal_donation
            + self.nmr_donation
        )
        registration_balance = self.registration_price
        nmr_balance = self.nmr_price
        paypal_donation_balance = self.paypal_donation
        for payment in self.payments:
            balance -= payment.amount
            registration_balance -= payment.registration_amount
            nmr_balance -= payment.nmr_amount
            paypal_donation_balance -= payment.paypal_donation_amount
        if balance < 0:
            balance = 0
        self.balance = balance
        if registration_balance < 0:
            registration_balance = 0
        self.registration_balance = registration_balance
        if nmr_balance < 0:
            nmr_balance = 0
        self.nmr_balance = nmr_balance
        if paypal_donation_balance < 0:
            paypal_donation_balance = 0
        self.paypal_donation_balance = paypal_donation_balance
    
    def get_invoice_items(self):
        reg_arrival_dict = {
            "03/14/2026":"Adult Pre-Registration Sat-Sun",
            "03/15/2026":"Adult Pre-Registration Sat-Sun",
            "03/16/2026":"Adult Pre-Registration Mon-Tues",
            "03/17/2026":"Adult Pre-Registration Mon-Tues",
            "03/18/2026":"Adult Pre-Registration Wed-Thurs",
            "03/19/2026":"Adult Pre-Registration Wed-Thurs",
            "03/20/2026":"Adult Pre-Registration Fri-Sat",
            "03/21/2026":"Adult Pre-Registration Fri-Sat",
        }
        items = []
        if self.age == '18+' and self.registration_balance > 0:
            items.append({
                'name':reg_arrival_dict[self.expected_arrival_date.strftime('%m/%d/%Y')],
                'description':'Gulf Wars Registration - ' + self.fname + ' ' + self.lname + ' - ' + self.expected_arrival_date.strftime('%m/%d/%Y'),
                'quantity':'1',
                'unit_amount':{
                    'currency_code':'USD',
                    'value':str(self.registration_balance)
                },
                'unit_of_measure': 'QUANTITY'
            })
        if self.nmr_balance > 0:
            items.append({
                'name':'NMR',
                'description':'Non-Member Fee - ' + self.fname + ' ' + self.lname,
                'quantity':'1',
                'unit_amount':{
                    'currency_code':'USD',
                    'value':str(self.nmr_balance)
                },
                'unit_of_measure': 'QUANTITY'
            })
        if self.paypal_donation_balance > 0:
            items.append({
                'name':'PayPal Donation',
                'description':'PayPal Donation - ' + self.fname + ' ' + self.lname,
                'quantity':'1',
                'unit_amount':{
                    'currency_code':'USD',
                    'value':str(self.paypal_donation_balance)
                },
                'unit_of_measure': 'QUANTITY'
            })
        return items


class Invoice(db.Model):
    __tablename__ = "invoice"
    invoice_number = db.Column(db.Integer(), primary_key=True)
    invoice_id = db.Column(db.String())
    invoice_type = db.Column(db.String(), nullable=False)
    invoice_email = db.Column(db.String(), nullable=False)
    invoice_date = db.Column(db.DateTime(), nullable=False)
    invoice_status = db.Column(db.String(), nullable=False)
    registration_total = db.Column(db.Integer(), default=0)
    nmr_total = db.Column(db.Integer(), default=0)
    donation_total = db.Column(db.Integer(), default=0)
    space_fee = db.Column(db.Numeric(10, 2), default=0)
    processing_fee = db.Column(db.Integer(), default=0)
    rider_fee = db.Column(db.Integer(), default=0)
    invoice_total = db.Column(
        db.Numeric(10, 2),
        Computed(
            registration_total
            + nmr_total
            + donation_total
            + space_fee
            + processing_fee
            + rider_fee
        ),
    )
    balance = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text())
    regs = db.relationship("Registrations", back_populates="invoice")
    merchants = db.relationship("Merchant", back_populates="invoice")
    earlyonrequests = db.relationship("EarlyOnRequest", back_populates="invoice")
    payments = db.relationship("Payment", back_populates="invoice")
    # event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    # event = db.relationship("Event", backref='invoice')

    def toJSON(self):
        data_dict = {}
        for key in self.__dict__:
            if not key.startswith("_"):
                if isinstance(self.__dict__[key], datetime):
                    data_dict[key] = datetime.strftime(self.__dict__[key], "%Y-%m-%d")
                else:
                    data_dict[key] = self.__dict__[key]
        return json.dumps(data_dict, sort_keys=True, default=str)

    def recalculate_balance(self):
        balance = (
            self.registration_total
            + self.nmr_total
            + self.donation_total
            + self.space_fee
            + self.processing_fee
            + self.rider_fee
        )
        for payment in self.payments:
            balance -= payment.amount
        if balance < 0:
            balance = 0
        self.balance = balance
        if self.balance > 0:
            self.invoice_status = "OPEN"

class Payment(db.Model):
    __tablename__ = "payment"
    id = db.Column(db.Integer(), primary_key=True)
    paypal_id = db.Column(db.String(), nullable=True)
    type = db.Column(db.String(), nullable=False)
    check_num = db.Column(db.Integer())
    payment_date = db.Column(db.DateTime(), nullable=False)
    registration_amount = db.Column(db.Integer(), default=0)
    nmr_amount = db.Column(db.Integer(), default=0)
    paypal_donation_amount = db.Column(db.Integer(), default=0)
    space_fee_amount = db.Column(db.Numeric(10, 2), default=0)
    processing_fee_amount = db.Column(db.Integer(), default=0)
    rider_fee_amount = db.Column(db.Integer(), default=0)
    electricity_fee_amount = db.Column(db.Numeric(10, 2), default=0)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    invoice_number = db.Column(db.Integer(), db.ForeignKey("invoice.invoice_number"))
    invoice = db.relationship("Invoice", back_populates="payments")
    reg_id = db.Column(db.Integer(), db.ForeignKey("registrations.id"))
    reg = db.relationship("Registrations", back_populates="payments")
    merchant_id = db.Column(db.Integer(), db.ForeignKey("merchant.id"))
    merchant = db.relationship("Merchant", back_populates="payments")
    earlyonrequest_id = db.Column(db.Integer(), db.ForeignKey("earlyonrequest.id"))
    earlyonrequest = db.relationship("EarlyOnRequest", back_populates="payments")
    # event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    # event = db.relationship("Event", backref='payment')

    def calculate_payment_amounts(self, payment_amount):
        # Registrations
        if self.reg is not None:
            # Check if Payment is enough to cover all costs
            if (
                payment_amount
                >= self.reg.registration_balance
                + self.reg.nmr_balance
                + self.reg.paypal_donation_balance
            ):
                self.registration_amount = self.reg.registration_balance
                self.nmr_amount = self.reg.nmr_balance
                self.paypal_donation_amount = self.reg.paypal_donation_balance
                self.amount = (
                    self.registration_amount
                    + self.nmr_amount
                    + self.paypal_donation_amount
                )
            # Registration Payment
            if payment_amount >= self.reg.registration_balance:
                payment_amount -= self.reg.registration_balance
                self.registration_amount = self.reg.registration_balance
            else:
                self.registration_amount = payment_amount
                payment_amount = 0
            # NMR Payment
            if payment_amount >= self.reg.nmr_balance:
                payment_amount -= self.reg.nmr_balance
                self.nmr_amount = self.reg.nmr_balance
            else:
                self.nmr_amount = payment_amount
                payment_amount = 0
            # PayPal Donation
            if payment_amount >= self.reg.paypal_donation_balance:
                payment_amount -= self.reg.paypal_donation_balance
                self.paypal_donation_amount = self.reg.paypal_donation_balance
            else:
                self.paypal_donation_amount = payment_amount
                payment_amount = 0

            self.amount = (
                self.registration_amount + self.nmr_amount + self.paypal_donation_amount
            )

        # Merchant
        if self.merchant is not None:
            # Check if Payment is enough to cover all costs
            if (
                payment_amount
                >= float(self.merchant.space_fee_balance)
                + self.merchant.processing_fee_balance
                + float(self.merchant.electricity_balance)
            ):
                self.space_fee_amount = self.merchant.space_fee_balance
                self.processing_fee_amount = self.merchant.processing_fee_balance
                self.electricity_fee_amount = self.merchant.electricity_balance
            # Space Fee Payment
            if payment_amount >= self.merchant.space_fee_balance:
                payment_amount -= float(self.merchant.space_fee_balance)
                self.space_fee_amount = float(self.merchant.space_fee_balance)
            else:
                self.space_fee_amount = payment_amount
                payment_amount = 0
            # Processing Fee Payment
            if payment_amount >= self.merchant.processing_fee_balance:
                payment_amount -= self.merchant.processing_fee_balance
                self.processing_fee_amount = self.merchant.processing_fee_balance
            else:
                self.processing_fee_amount = payment_amount
                payment_amount = 0
            # Electricity Fee Payment
            if payment_amount >= self.merchant.electricity_balance:
                payment_amount -= float(self.merchant.electricity_balance)
                self.electricity_fee_amount = float(self.merchant.electricity_balance)
            else:
                self.electricity_fee_amount = float(payment_amount)
                payment_amount = 0

            self.amount = (
                float(self.space_fee_amount)
                + self.processing_fee_amount
                + float(self.electricity_fee_amount)
            )

        # EarlyOn
        if self.earlyonrequest is not None:
            # Check if Payment is enough to cover all costs
            if payment_amount >= self.earlyonrequest.rider_balance:
                self.rider_fee_amount = self.earlyonrequest.rider_balance
            # Rider Fee Payment
            if payment_amount >= self.earlyonrequest.rider_balance:
                payment_amount -= self.earlyonrequest.rider_balance
                self.rider_fee_amount = self.earlyonrequest.rider_balance
            else:
                self.rider_fee_amount = payment_amount
                payment_amount = 0

            self.amount = self.rider_fee_amount


class RegLogs(db.Model):
    __tablename__ = "reglogs"
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer(), db.ForeignKey("registrations.id"))
    userid = db.Column(db.Integer(), db.ForeignKey("users.id"))
    timestamp = db.Column(db.DateTime())
    action = db.Column(db.String())
    # event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    # event = db.relationship("Event", backref='reglogs')


class MarshalInspection(db.Model):
    __tablename__ = "marshal_inspection"
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer, db.ForeignKey("registrations.id"))
    inspection_type = db.Column(db.String())
    inspection_date = db.Column(db.DateTime())
    inspecting_marshal_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    inspecting_marshal = db.relationship("User", foreign_keys=[inspecting_marshal_id])
    inspected = db.Column(db.Boolean())


class Bows(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    poundage = db.Column(db.Double())
    bow_inspection_date: so.Mapped[Optional[datetime]]
    bow_inspection_marshal_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    bow_inspection_marshal = db.relationship(
        "User", foreign_keys=[bow_inspection_marshal_id]
    )

    def __repr__(self):
        return "<Bow {}>".format(self.id)


class RegBows(db.Model):
    __tablename__ = "reg_bows"
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(
        db.Integer(), db.ForeignKey("registrations.id", ondelete="CASCADE")
    )
    bowid = db.Column(db.Integer(), db.ForeignKey("bows.id", ondelete="CASCADE"))


class Crossbows(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    inchpounds = db.Column(db.Double())
    crossbow_inspection_date: so.Mapped[Optional[datetime]]
    crossbow_inspection_marshal_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    crossbow_inspection_marshal = db.relationship(
        "User", foreign_keys=[crossbow_inspection_marshal_id]
    )

    def __repr__(self):
        return "<CrossBow {}>".format(self.id)


class RegCrossBows(db.Model):
    __tablename__ = "reg_crossbows"
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(
        db.Integer(), db.ForeignKey("registrations.id", ondelete="CASCADE")
    )
    crossbowid = db.Column(
        db.Integer(), db.ForeignKey("crossbows.id", ondelete="CASCADE")
    )


class IncidentReport(db.Model):
    __tablename__ = "incidentreport"
    id = db.Column(db.Integer(), primary_key=True)
    regid = db.Column(db.Integer, db.ForeignKey("registrations.id"))
    report_date = db.Column(db.DateTime())
    incident_date = db.Column(db.DateTime())
    reporting_user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    reporting_user = db.relationship("User", foreign_keys=[reporting_user_id])
    notes = db.Column(db.Text())
    # event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    # event = db.relationship("Event", backref='incidentreport')


class PriceSheet(db.Model):
    __tablename__ = "pricesheet"
    arrival_date = db.Column(db.Date(), primary_key=True)
    prereg_price = db.Column(db.Integer())
    atd_price = db.Column(db.Integer())
    # event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    # event = db.relationship("Event", backref='pricesheet')


class Kingdom(db.Model):
    __tablename__ = "kingdom"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)


class Lodging(db.Model):
    __tablename__ = "lodging"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    # event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    # event = db.relationship("Event", backref='lodging')


# class Event(db.Model):
#     __tablename__ = 'event'
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(), nullable=False)
#     year = db.Column(db.Integer(), nullable=False)
#     start_date = db.Column(db.Date(), nullable=False)
#     end_date = db.Column(db.Date(), nullable=False)
#     location = db.Column(db.String(), nullable=False)
#     description = db.Column(db.Text(), nullable=False)


class Merchant(db.Model):
    __tablename__ = "merchant"
    id = db.Column(db.Integer(), primary_key=True)
    status = db.Column(db.String(), nullable=False, default="PENDING")
    business_name = db.Column(db.String(), nullable=False)
    sca_name = db.Column(db.String(), nullable=False)
    fname = db.Column(db.String(), nullable=False)
    lname = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(), nullable=False)
    text_permission = db.Column(db.Boolean(), default=False)
    address = db.Column(db.String(), nullable=False)
    city = db.Column(db.String())
    state_province = db.Column(db.String())
    zip = db.Column(db.Integer())
    frontage_width = db.Column(db.Integer(), nullable=False, default=0)
    frontage_depth = db.Column(db.Integer(), nullable=False, default=0)
    ropes_front = db.Column(db.Integer(), nullable=False, default=0)
    ropes_back = db.Column(db.Integer(), nullable=False, default=0)
    ropes_left = db.Column(db.Integer(), nullable=False, default=0)
    ropes_right = db.Column(db.Integer(), nullable=False, default=0)
    personal_space = db.Column(db.Numeric(10, 2), nullable=True, default=0.0)
    extra_space = db.Column(db.Numeric(10, 2), nullable=True, default=0.0)
    space_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    space_fee_balance = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    additional_space_information = db.Column(db.Text())
    processing_fee = db.Column(db.Integer(), nullable=False, default=0)
    processing_fee_balance = db.Column(db.Integer(), nullable=False, default=0)
    merchant_fee = db.Column(db.Numeric(10, 2), nullable=False)
    electricity_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    electricity_balance = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    electricity_request = db.Column(db.Text(), nullable=True)
    food_merchant_agreement = db.Column(db.Boolean(), default=False)
    estimated_date_of_arrival = db.Column(db.Date(), nullable=False)
    service_animal = db.Column(db.Boolean(), default=False)
    last_3_years = db.Column(db.Boolean(), default=False)
    vehicle_length = db.Column(db.Integer(), nullable=True)
    vehicle_license_plate = db.Column(db.String(), nullable=True)
    vehicle_state = db.Column(db.String(), nullable=True)
    trailer_length = db.Column(db.Integer(), nullable=True)
    trailer_license_plate = db.Column(db.String(), nullable=True)
    trailer_state = db.Column(db.String(), nullable=True)
    notes = db.Column(db.Text(), nullable=True)

    application_date = db.Column(
        db.DateTime(),
        default=lambda: datetime.now(pytz.timezone("America/Chicago"))
        .replace(microsecond=0)
        .isoformat(),
    )

    checkin_date = db.Column(db.DateTime(), nullable=True)

    # LEGAL
    signature = db.Column(db.String(), nullable=True)

    # Relationships
    invoice_number = db.Column(db.Integer(), db.ForeignKey("invoice.invoice_number"))
    invoice = db.relationship("Invoice", back_populates="merchants")
    payments = db.relationship("Payment", back_populates="merchant")

    # event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    # event = db.relationship("Event", backref='merchants')

    def __repr__(self):
        return "<Merchant {}>".format(self.business_name)
    
    def toJSON(self):
        data_dict = {}
        for key in self.__dict__:
            if not key.startswith("_"):
                if isinstance(self.__dict__[key], datetime):
                    data_dict[key] = datetime.strftime(self.__dict__[key], "%Y-%m-%d")
                else:
                    data_dict[key] = self.__dict__[key]
        return json.dumps(data_dict, sort_keys=True, default=str)

    def recalculate_balance(self):
        balance = float(self.space_fee) + self.processing_fee + float(self.electricity_fee)
        space_fee_balance = float(self.space_fee)
        processing_fee_balance = self.processing_fee
        electricity_balance = float(self.electricity_fee)
        for payment in self.payments:
            balance -= payment.space_fee_amount
            balance -= payment.processing_fee_amount
            space_fee_balance -= payment.space_fee_amount
            processing_fee_balance -= payment.processing_fee_amount
            electricity_balance -= payment.electricity_fee_amount
        if balance < 0:
            self.balance = 0
        self.balance = balance
        if space_fee_balance < 0:
            self.space_fee_balance = 0
        self.space_fee_balance = space_fee_balance
        if processing_fee_balance < 0:
            self.processing_fee_balance = 0
        self.processing_fee_balance = processing_fee_balance
        if electricity_balance < 0:
            self.electricity_balance = 0
        self.electricity_balance = electricity_balance

    def get_invoice_items(self):
        items = []
        if self.space_fee_balance > 0:
            items.append({
                'name':'Space Fee',
                'description':'Gulf Wars Merchant Space Fee',
                'quantity':'1',
                'unit_amount':{
                    'currency_code':'USD',
                    'value':str(self.space_fee_balance)
                },
                'unit_of_measure': 'QUANTITY'
            })
        if self.processing_fee_balance > 0:
            items.append({
                'name':'Processing Fee',
                'description':'Gulf Wars Merchant Processing Fee',
                'quantity':'1',
                'unit_amount':{
                    'currency_code':'USD',
                    'value':str(self.processing_fee_balance)
                },
                'unit_of_measure': 'QUANTITY'
            })
        if self.electricity_balance > 0:
            items.append({
                'name':'Electricity Fee',
                'description':'Gulf Wars Merchant Electricity Fee',
                'quantity':'1',
                'unit_amount':{
                    'currency_code':'USD',
                    'value':str(self.electricity_balance)
                },
                'unit_of_measure': 'QUANTITY'
            })
        return items

class ScheduledEvent(db.Model):
    __tablename__ = "scheduledevent"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    start_datetime = db.Column(db.DateTime())
    end_datetime = db.Column(db.DateTime())
    instructor = db.Column(db.String())
    short_description = db.Column(db.Text())
    description = db.Column(db.Text())
    location = db.Column(db.String())
    topic_id = db.Column(db.Integer(), db.ForeignKey("topic.id"))
    topic = db.relationship("Topic", backref="scheduledevent_topic", viewonly=True)
    tags = db.relationship("Tag", secondary="scheduledevent_tags")
    user_instructor_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    user_instructor = db.relationship("User", backref="user_instructor", viewonly=True)


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())


class ScheduledEvent_Tags(db.Model):
    __tablename__ = "scheduledevent_tags"
    id = db.Column(db.Integer(), primary_key=True)
    scheduledevent_id = db.Column(
        db.Integer(), db.ForeignKey("scheduledevent.id", ondelete="CASCADE")
    )
    tag_id = db.Column(db.Integer(), db.ForeignKey("tag.id", ondelete="CASCADE"))


class Topic(db.Model):
    __tablename__ = "topic"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())


class User_ScheduledEvents(db.Model):
    __tablename__ = "user_scheduledevents"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    scheduledevent_id = db.Column(
        db.Integer(), db.ForeignKey("scheduledevent.id", ondelete="CASCADE")
    )