from flask_wtf import FlaskForm
from app.utils.db_utils import *
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, HiddenField, SelectMultipleField, TextAreaField, DecimalField, FieldList, FormField, DateTimeField, FileField, FloatField, widgets
from wtforms.fields import DateField, DateTimeLocalField, DateTimeField
from wtforms.validators import DataRequired, Email, InputRequired, Optional, ValidationError, NoneOf, EqualTo, Length, NumberRange

import pandas as pd
from datetime import datetime
import uuid

agedata = [('-','-'),('18+', 'Adult 18+'), ('13-17', 'Teen 13 - 17'), ('6-12', 'Youth 6 - 12'), ('0-5', 'Child 0 - 5'),('Royals','Royals')]

mbrdata = [('-','-'),('Member', 'Member'), ('Non-Member', 'Non-Member')]

reporttypedata = [('royal_registrations', 'royal_registrations'), ('land_pre-reg', 'land_pre-reg'), ('full_export', 'full_export'), ('full_signatue_export', 'full_signature_export'), ('full_checkin_report', 'full_checkin_report'), ('at_door_count', 'at_door_count'), ('kingdom_count', 'kingdom_count'), ('ghost_report', 'ghost_report'), ('earlyon','early_on_report'), ('paypal_paid_export','paypal_paid_export'),('paypal_canceled_export','paypal_canceled_export'),('paypal_recon_export','paypal_recon_export'),('atd_export','atd_export'),('log_export','log_export'),('minor_waivers','minor_waivers')]

paymentdata = [('',''),('cash','Cash'), ('zettle','Zettle'),('travlers_check','Travlers Check')]

preregstatusdata = [('',''),('SUCCEEDED','SUCCEEDED')]

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class RequiredIfMembership(InputRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIfMembership, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if other_field.data == 'Member':
            super(RequiredIfMembership, self).__call__(form, field)
        else:
            Optional(self.message).__call__(form, field)

class RequiredIf(InputRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)
        else:
            Optional(self.message).__call__(form, field)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateUserForm(FlaskForm):
    # id = StringField('User Id', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    role = MultiCheckboxField('Role', validators=[DataRequired()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    department = SelectField('Department', validators=[DataRequired()], choices=[])
    # event = SelectField('Event', validators=[])
    medallion = IntegerField('Medallion')
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def populate_object(self, obj):
        # Username - Strip - Lower
        if self.username.data:
            obj.username = self.username.data.strip().lower()
        # Roles - Iterate
        for roleid in self.role.data:
            obj.roles.append(get_role(roleid))
        # First Name - Strip
        if self.fname.data:
            obj.fname = self.fname.data.strip()
        # Last Name - Strip
        if self.lname.data:
            obj.lname = self.lname.data.strip()
        # Department - Check '-'
        if self.department.data and self.department.data != 'None':
            obj.department_id = self.department.data
        # Medallion 
        if self.medallion.data:
            obj.medallion = self.medallion.data
        # Password - Strip - Hash
        if self.password.data:
            obj.set_password(self.password.data.strip())
        # Active
        obj.active = True
        #FS Uniqueifier
        obj.fs_uniquifier = uuid.uuid4().hex

class RegisterUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords Must Match')])
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords Must Match'), Length(min=6, max=32, message='Password length must be between 6 and 32 characters')])
    submit = SubmitField('Submit')

    def populate_object(self, obj):
        # Username - Strip - Lower
        if self.username.data:
            obj.username = self.username.data.strip().lower()
        # First Name - Strip
        if self.fname.data:
            obj.fname = self.fname.data.strip()
        # Last Name - Strip
        if self.lname.data:
            obj.lname = self.lname.data.strip()
        # Email - Strip - Lower
        if self.lname.data:
            obj.lname = self.lname.data.strip().lower()         
        # Password - Strip - Hash
        if self.password.data:
            obj.set_password(self.password.data.strip())
        # Active
        obj.active = True
        #FS Uniqueifier
        obj.fs_uniquifier = uuid.uuid4().hex

class CreateRoleForm(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired()])
    role_name = StringField('Role Name', validators=[DataRequired()])
    permissions = MultiCheckboxField('Permissions')
    submit = SubmitField('Submit')



# class CreateEventForm(FlaskForm):
#     event_name = StringField('Event Name', validators=[DataRequired()])
#     event_year = IntegerField('Event Year', validators=[DataRequired()])
#     event_description = TextAreaField('Event Description', validators=[DataRequired()])
#     event_start = DateField('Event Start', format='%Y-%m-%d', validators=[DataRequired()])
#     event_end = DateField('Event End', format='%Y-%m-%d', validators=[DataRequired()])
#     event_location = StringField('Event Location', validators=[DataRequired()])
#     submit = SubmitField('Submit')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    role = MultiCheckboxField('Role', validators=[Optional()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    department = SelectField('Department', validators=[DataRequired()], choices=[])
    # event = SelectField('Event', validators=[])
    medallion = IntegerField('Medallion', validators=[Optional()])
    active = BooleanField('Active')
    submit = SubmitField('Submit')

    def populate_object(self, obj):
        # Username - Strip - Lower
        if self.username.data:
            obj.username = self.username.data.strip().lower()
        # Roles - Iterate
        current_role_ids = []
        user_role_permissions = [str(r[0]) for r in get_role_choices()]
        for role in obj.roles:
            current_role_ids.append(str(role.id))
        for roleid in self.role.data:
            if roleid in user_role_permissions and roleid not in current_role_ids:
                obj.roles.append(get_role(roleid))
        for roleid in current_role_ids:
            if roleid in user_role_permissions and roleid not in self.role.data:
                obj.roles.remove(get_role(roleid))
        # First Name - Strip
        if self.fname.data:
            obj.fname = self.fname.data.strip()
        # Last Name - Strip
        if self.lname.data:
            obj.lname = self.lname.data.strip()
        # Department - Check '-'
        if self.department.data and self.department.data != 'None':
            obj.department_id = self.department.data
        # Medallion 
        if self.medallion.data:
            obj.medallion = self.medallion.data
        # Active
        obj.active = self.active.data

    def populate_form(self, obj):
        # Username
        if obj.username:
            self.username.data = obj.username
        # Roles - Iterate
        if obj.roles:
            role_array = []
            for role in obj.roles:
                role_array.append(str(role.id))
            self.role.data = role_array
        # First Name
        if obj.fname:
            self.fname.data = obj.fname
        # Last Name
        if obj.lname:
            self.lname.data = obj.lname
        # Department
        if obj.department_id:
            self.department.data = str(obj.department_id)
        # Medallion 
        if obj.medallion:
            self.medallion.data = obj.medallion
        # Active
        self.active.data = obj.active

class UpdatePasswordForm(FlaskForm):
    confirm = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords Must Match')])
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords Must Match'), Length(min=6, max=32, message='Password length must be between 6 and 32 characters')])
    submit = SubmitField('Reset Password')
    def populate_object(self, obj):
        # Password - Strip - Hash
        # Password - Strip - Hash
        if self.password.data:
            obj.set_password(self.password.data.strip())

class CreateRegForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    scaname = StringField('SCA Name', validators=[])
    kingdom = SelectField('Kingdom', validators=[NoneOf('-', message='You must select a Kingdom')])
    lodging = SelectField('Camping Group', validators=[NoneOf('-', message='You must select a Lodging')])
    age = SelectField('Age Range', validators=[NoneOf('-', message='You must select an Age Range')], choices=agedata)
    mbr = SelectField('Membership Status', validators=[NoneOf('-', message='You must select a Membership Status')], choices=mbrdata)
    mbr_num = IntegerField('Membership #', validators=[RequiredIfMembership('mbr')])
    mbr_num_exp = DateField('Exp Date', validators=[RequiredIfMembership('mbr')])
    zip = IntegerField('Zip', validators=[Optional()])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),Email()])
    emergency_contact_name = StringField('Legal Name', validators=[DataRequired()])
    emergency_contact_phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def populate_object(self, obj):
        # First Name - Strip
        if self.fname.data:
            obj.fname = self.fname.data.strip()
        # Last Name - Strip
        if self.lname.data:
            obj.lname = self.lname.data.strip()
        # SCA Name - Strip
        if self.scaname.data:
            obj.scaname = self.scaname.data.strip()
        # Kingdom
        if self.kingdom.data:
            obj.kingdom_id = self.kingdom.data
        # Lodging
        if self.lodging.data:
            obj.lodging_id = self.lodging.data
        # Age
        if self.age.data:
            obj.age = self.age.data
        # Member
        if self.mbr.data:
            obj.mbr = True if self.mbr.data == 'Member' else False
        # Member Number
        if self.mbr_num.data:
            obj.mbr_num = self.mbr_num.data
        # Member Expiration
        if self.mbr_num_exp.data:
            obj.mbr_num_exp = self.mbr_num_exp.data
        # Zip
        if self.zip.data:
            obj.zip = self.zip.data
        # Phone
        if self.phone.data:
            obj.phone = self.phone.data
        # Email
        if self.email.data:
            obj.email = self.email.data
        # Emergency Contact Name
        if self.emergency_contact_name.data:
            obj.emergency_contact_name = self.emergency_contact_name.data
        # Emergency Contact Phone
        if self.emergency_contact_phone.data:
            obj.emergency_contact_phone = self.emergency_contact_phone.data
        # Expected Arrival Date - Set to Today
        obj.expected_arrival_date = datetime.now(pytz.timezone('America/Chicago')).date()
        # Actual Arrival Date - Set to Today
        obj.actual_arrival_date = datetime.now(pytz.timezone('America/Chicago')).date()
        # Registration Price/Balance + NMR Price/Balance + PayPal Donation/Balance + Balance
        if obj.age == '18+':
            registration_price = get_atd_pricesheet_day(obj.actual_arrival_date)
            obj.registration_price = registration_price
            obj.registration_balance = registration_price
            if obj.mbr != True:
                obj.nmr_price = 10
                obj.nmr_balance = 10
            else:
                obj.nmr_price = 0
                obj.nmr_balance = 0
        else:
            obj.registration_price = 0
            obj.registration_balance = 0
            obj.nmr_price = 0
            obj.nmr_balance = 0
            
        obj.paypal_donation = 0
        obj.paypal_donation_balance = 0
        
        obj.balance = obj.registration_price + obj.nmr_price + obj.paypal_donation

class CreatePreRegForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    scaname = StringField('SCA Name', validators=[])
    city = StringField('City', validators=[DataRequired()])
    state_province = StringField('State/Province', validators=[DataRequired()])
    zip = IntegerField('Zip', validators=[DataRequired(),NumberRange(min=0,max=99999,message="Zip Code must match ##### format")])
    country = StringField('Country', validators=[DataRequired()], default='United States')
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Communication Email', validators=[DataRequired(),Email()])
    invoice_email = StringField('Invoice Email', validators=[DataRequired(),Email()])
    kingdom = SelectField('Kingdom', validators=[NoneOf('-', message='You must select a Kingdom')])
    lodging = SelectField('Camping Group', validators=[NoneOf('-', message='You must select a Lodging')])
    emergency_contact_name = StringField('Legal Name', validators=[DataRequired()])
    emergency_contact_phone = StringField('Phone', validators=[DataRequired()])
    age = SelectField('Age Range', validators=[NoneOf('-', message='You must select an Age Range')], id='age', choices=agedata)
    mbr = SelectField('Membership Status', validators=[NoneOf('-', message='You must select a Membership Status')], choices=mbrdata)
    mbr_num = IntegerField('Membership #', validators=[RequiredIfMembership('mbr')])
    mbr_num_exp = DateField('Exp Date', validators=[RequiredIfMembership('mbr')])
    expected_arrival_date = SelectField('Arrival Date', validators=[NoneOf('-', message='You must select an Arrival Date')])
    paypal_donation = BooleanField('Please check here if you would like to <b>DONATE</b> to cover your Paypal processing fees.', validators=[])
    paypal_donation_amount = IntegerField("PayPal Donation Amount", default=5)
    royal_departure_date = DateField('Departure Date', validators=[Optional()])
    royal_title = StringField('Royal Title', validators=[Optional()])
    submit = SubmitField('Register')

    def populate_object(self, obj):
        # First Name - Strip
        if self.fname.data:
            obj.fname = self.fname.data.strip()
        # Last Name - Strip
        if self.lname.data:
            obj.lname = self.lname.data.strip()
        # SCA Name - Strip
        if self.scaname.data:
            obj.scaname = self.scaname.data.strip()
        # Zip
        if self.zip.data:
            obj.zip = self.zip.data
        # City - Strip
        if self.city.data:
            obj.city = self.city.data.strip()
        # State/Province - Strip
        if self.state_province.data:
            obj.state_province = self.state_province.data.strip()
        # Country - Strip
        if self.country.data:
            obj.country = self.country.data.strip()
        # Phone
        if self.phone.data:
            obj.phone = self.phone.data
        # Email - Strip - Lower
        if self.email.data:
            obj.email = self.email.data.strip().lower()
        # Invoice Email - Strip - Lower
        if self.invoice_email.data:
            obj.invoice_email = self.invoice_email.data.strip().lower()
        # Kingdom
        if self.kingdom.data:
            obj.kingdom_id = self.kingdom.data
        # Lodging
        if self.lodging.data:
            obj.lodging_id = self.lodging.data
        # Age
        if self.age.data:
            obj.age = self.age.data
        # Member
        if self.mbr.data:
            obj.mbr = True if self.mbr.data == 'Member' else False
        # Member Number
        if self.mbr_num.data:
            obj.mbr_num = self.mbr_num.data
        # Member Expiration
        if self.mbr_num_exp.data:
            obj.mbr_num_exp = self.mbr_num_exp.data
        # Expected Arrival
        if self.expected_arrival_date.data:
            obj.expected_arrival_date = self.expected_arrival_date.data
        # Royal Departure
        if self.royal_departure_date.data:
            obj.royal_departure_date = self.royal_departure_date.data
        # Royal Tital
        if self.royal_title.data:
            obj.royal_title = self.royal_title.data
        # Emergency Contact Name
        if self.emergency_contact_name.data:
            obj.emergency_contact_name = self.emergency_contact_name.data
        # Emergency Contact Phone
        if self.emergency_contact_phone.data:
            obj.emergency_contact_phone = self.emergency_contact_phone.data
        # Pre-Registration
        obj.prereg = True
        # Prices
        # Registration Price/Balance + NMR Price/Balance
        if obj.age == '18+':
            registration_price = get_prereg_pricesheet_day(obj.expected_arrival_date)
            obj.registration_price = registration_price
            obj.registration_balance = registration_price
            if not obj.mbr:
                obj.nmr_price = 10
                obj.nmr_balance = 10
            else:
                obj.nmr_price = 0
                obj.nmr_balance = 0
        else:
            obj.registration_price = 0
            obj.registration_balance = 0
            obj.nmr_price = 0
            obj.nmr_balance = 0
        # PayPal Donation/Balance
        if self.paypal_donation.data == True:
            obj.paypal_donation = self.paypal_donation_amount.data
            obj.paypal_donation_balance = self.paypal_donation_amount.data
        else:
            obj.paypal_donation = 0
            obj.paypal_donation_balance = 0
        # Balance
        obj.balance = obj.registration_balance + obj.nmr_balance + obj.paypal_donation_balance

        

class CheckinForm(FlaskForm):
    regid = IntegerField()
    fname = StringField('First Name')
    lname = StringField('Last Name')
    scaname = StringField('SCA Name')
    kingdom = SelectField('Kingdom', validators=[NoneOf('-', message='You must select a Kingdom')])
    lodging = SelectField('Camping Group', validators=[NoneOf('-', message='You must select a Lodging')])
    age = SelectField('Age Range', validators=[NoneOf('-', message='You must select an Age Range')], choices=agedata)
    mbr = SelectField('Membership Status', validators=[NoneOf('-', message='You must select a Membership Status')], choices=mbrdata)
    mbr_num = IntegerField('Membership Number', validators=[RequiredIfMembership('mbr')])
    mbr_num_exp = DateField('Membership Expiration Date', validators=[RequiredIfMembership('mbr')])
    medallion = IntegerField('Medallion #', validators=[DataRequired()])
    minor_waiver = SelectField('Minor Waiver', validators=[Optional(), NoneOf('-', message='You must select a Minor Form Validation')], choices=[('-','-'),('Signed by Parent/Guardian','Signed by Parent/Guardian'),('Medical Authorization Form Submitted','Medical Authorization Form Submitted')])
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit')

class EditForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    scaname = StringField('SCA Name')
    city = StringField('City')
    state_province = StringField('State/Province')
    zip = IntegerField('Zip Code')
    country = StringField('Country', default='United States')
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Communication Email', validators=[DataRequired()])
    invoice_email = StringField('Invoice Email', validators=[DataRequired()])
    age = SelectField('Age Range', validators=[NoneOf('-', message='You must select an Age Range')], choices=agedata)
    emergency_contact_name = StringField('Name', validators=[DataRequired()])
    emergency_contact_phone = StringField('Phone', validators=[DataRequired()])
    mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    mbr_num = IntegerField('Member Number', validators=[RequiredIfMembership('mbr')])
    mbr_num_exp = DateField('Member Exp Date', validators=[RequiredIfMembership('mbr')])
    
    reg_date_time = DateTimeField('Registration Date/Time')
    prereg = BooleanField('Pre-Registered')
    expected_arrival_date = SelectField('Arrival Date', validators=[NoneOf('-', message='You must select an Arrival Date')])
    early_on = BooleanField('Early On')
    notes = TextAreaField('Notes')
    duplicate = BooleanField('Duplicate Registration')

    paypal_donation = IntegerField('PayPal Donation', validators=[NumberRange(min=0,max=999)], default=0)
    
    checkin = DateTimeField('Checkin Date/Time', validators=[Optional()])
    medallion = IntegerField('Medallion #', validators=[Optional()])
    actual_arrival_date = DateField('Actual Arrival Date')

    kingdom = SelectField('Kingdom', validators=[DataRequired()])
    lodging = SelectField('Camping Group', validators=[DataRequired()])

    #mbr_exp
    submit = SubmitField('Submit')

    def populate_form(self, obj):
        for field in self._fields:
            print(field)
        # First Name
        if obj.fname:
            self.fname.data = obj.fname
        # Last Name
        if obj.lname:
            self.lname.data = obj.lname
        # SCA Name
        if obj.scaname:
            self.scaname.data = obj.scaname
        # Zip
        if obj.zip:
            self.zip.data = obj.zip
        # City
        if obj.city:
            self.city.data = obj.city
        # State/Province
        if obj.state_province:
            self.state_province.data = obj.state_province
        # Country
        if obj.country:
            self.country.data = obj.country
        # Phone
        if obj.phone:
            self.phone.data = obj.phone
        # Email
        if obj.email:
            self.email.data = obj.email
        # Invoice Email
        if obj.invoice_email:
            self.invoice_email.data = obj.invoice_email
        # Kingdom
        if obj.kingdom_id:
            self.kingdom.data = str(obj.kingdom_id)
        # Lodging
        if obj.lodging_id:
            self.lodging.data = str(obj.lodging_id)
        # Age
        if obj.age:
            self.age.data = obj.age
        # Member
        self.mbr.data = 'Member' if obj.mbr == True else 'Non-Member'
        # Member Number
        if obj.mbr_num:
            self.mbr_num.data = obj.mbr_num
        # Member Expiration
        if obj.mbr_num_exp:
            self.mbr_num_exp.data = obj.mbr_num_exp
        # Expected Arrival
        if obj.expected_arrival_date:
            self.expected_arrival_date.data = obj.expected_arrival_date.strftime('%Y/%m/%d')       
        # Emergency Contact Name
        if obj.emergency_contact_name:
            self.emergency_contact_name.data = obj.emergency_contact_name 
        # Emergency Contact Phone
        if obj.emergency_contact_phone:
            self.emergency_contact_phone.data = obj.emergency_contact_phone 
        # Pre-Registration
        self.prereg.data = obj.prereg 
        # EarlyOn Approved
        self.early_on.data = obj.early_on_approved
        # Duplicate
        self.duplicate.data = obj.duplicate
        # Notes
        if obj.notes:
            self.notes.data = obj.notes         
        # Medallion
        if obj.medallion:
            self.medallion.data = obj.medallion
        # Prices
        # PayPal Donation
        if obj.paypal_donation:
            self.paypal_donation.data = obj.paypal_donation         

    def populate_object(self, obj):
        # First Name - Strip
        if self.fname.data:
            obj.fname = self.fname.data.strip()
        # Last Name - Strip
        if self.lname.data:
            obj.lname = self.lname.data.strip()
        # SCA Name - Strip
        if self.scaname.data:
            obj.scaname = self.scaname.data.strip()
        # Zip
        if self.zip.data:
            obj.zip = self.zip.data
        # City - Strip
        if self.city.data:
            obj.city = self.city.data.strip()
        # State/Province - Strip
        if self.state_province.data:
            obj.state_province = self.state_province.data.strip()
        # Country - Strip
        if self.country.data:
            obj.country = self.country.data.strip()
        # Phone
        if self.phone.data:
            obj.phone = self.phone.data
        # Email - Strip - Lower
        if self.email.data:
            obj.email = self.email.data.strip().lower()
        # Invoice Email - Strip - Lower
        if self.invoice_email.data:
            obj.invoice_email = self.invoice_email.data.strip().lower()
        # Kingdom
        if self.kingdom.data:
            obj.kingdom_id = self.kingdom.data
        # Lodging
        if self.lodging.data:
            obj.lodging_id = self.lodging.data
        # Age
        if self.age.data:
            obj.age = self.age.data
        # Member
        if self.mbr.data:
            obj.mbr = True if self.mbr.data == 'Member' else False
        # Member Number
        if self.mbr_num.data:
            obj.mbr_num = self.mbr_num.data
        # Member Expiration
        if self.mbr_num_exp.data:
            obj.mbr_num_exp = self.mbr_num_exp.data
        # Expected Arrival
        if self.expected_arrival_date.data:
            obj.expected_arrival_date = self.expected_arrival_date.data

        # Emergency Contact Name
        if self.emergency_contact_name.data:
            obj.emergency_contact_name = self.emergency_contact_name.data
        # Emergency Contact Phone
        if self.emergency_contact_phone.data:
            obj.emergency_contact_phone = self.emergency_contact_phone.data
        # Pre-Registration
        obj.prereg = self.prereg.data
        # EarlyOn Approved
        obj.early_on_approved = self.early_on.data
        # Duplicate
        obj.duplicate = self.duplicate.data
        # Notes
        if self.notes.data:
            obj.notes = self.notes.data
        # Medallion
        if self.medallion.data:
            obj.medallion = self.medallion.data
        # Prices
        if obj.age == '18+':
            if obj.prereg == True:
                registration_price = get_prereg_pricesheet_day(obj.actual_arrival_date if obj.actual_arrival_date else obj.expected_arrival_date)
            else:
                registration_price = get_atd_pricesheet_day(obj.actual_arrival_date)
            obj.registration_price = registration_price
            if obj.mbr != True:
                obj.nmr_price = 10
            else:
                obj.nmr_price = 0
        else:
            obj.registration_price = 0
            obj.nmr_price = 0
            
        obj.paypal_donation = self.paypal_donation.data
        
        obj.balance = obj.registration_price + obj.nmr_price + obj.paypal_donation
        obj.recalculate_balance()

class EditLimitedForm(FlaskForm):
    age = SelectField('Age Range', validators=[NoneOf('-', message='You must select an Age Range')], choices=agedata)
    mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    mbr_num = IntegerField('Member Number')
    mbr_num_exp = DateField('Member Exp Date')
    medallion = IntegerField('Medallion #', validators=[DataRequired()])
    kingdom = SelectField('Kingdom', validators=[DataRequired()])
    lodging = SelectField('Camping Group', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit')

    def populate_form(self, obj):
        # Member
        self.mbr.data = 'Member' if obj.mbr else 'Non-Member'
        # Member Number
        if obj.mbr_num:
            self.mbr_num.data = obj.mbr_num
        # Member Expiration
        if obj.mbr_num_exp:
            self.mbr_num_exp.data = obj.mbr_num_exp
        # Medallion
        if obj.medallion:
            self.medallion.data = obj.medallion
        # Notes
        if obj.notes:
            self.notes.data = obj.notes

    def populate_object(self, obj):
        # Member
        if self.mbr.data:
            obj.mbr = True if self.mbr.data == 'Member' else False
        # Member Number
        if self.mbr_num.data:
            obj.mbr_num = self.mbr_num.data
        # Member Expiration
        if self.mbr_num_exp.data:
            obj.mbr_num_exp = self.mbr_num_exp.data
        # Medallion
        if self.medallion.data:
            obj.medallion = self.medallion.data
        # Notes
        if self.notes.data:
            obj.notes = self.notes.data
        
class RiderForm(Form):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    scaname = StringField('SCA Name', validators=[Optional()])
    minor = BooleanField('Minor', default=False, validators=[Optional()])
    regid = IntegerField('Registration Id', validators=[DataRequired()])
    submit = SubmitField('Add Rider')

class EarlyOnForm(FlaskForm):
    arrival_date = SelectField('Estimated Date of Arrival', validators=[NoneOf('-', message='You must select an Arrival Date')])
    department = SelectField('Department', validators=[DataRequired()], choices=[])
    notes = TextAreaField('Notes')
    riders = FieldList(FormField(RiderForm), min_entries=0, max_entries=10)
    submit = SubmitField('Submit Early On Request')

class EarlyOnApprovalForm(FlaskForm):
    arrival_date = SelectField('Estimated Date of Arrival', validators=[NoneOf('-', message='You must select an Arrival Date')])
    department = SelectField('Department', validators=[NoneOf('-', message='You must select a Department')], choices=[])
    notes = TextAreaField('Notes')
    riders = FieldList(FormField(RiderForm), min_entries=0, max_entries=10)
    dept_approval_status = SelectField('Department Approval', choices=[('PENDING','PENDING'),('APPROVED','APPROVED'),('DENIED','DENIED')])
    autocrat_approval_status = SelectField('Autocrat Approval', choices=[('PENDING','PENDING'),('APPROVED','APPROVED'),('DENIED','DENIED')])
    submit = SubmitField('Submit Early On Request')

class UpdateInvoiceForm(FlaskForm):
    invoice_amount = FloatField('Invoice Amount')
    registration_amount = IntegerField('Registration Amount')
    invoice_email = StringField('Invoice Email')
    invoice_number = IntegerField('Invoice Number', validators=[])
    invoice_status = SelectField('Invoice Status', choices=[('UNSENT','UNSENT'),('OPEN','OPEN'),('PAID','PAID'),('NO PAYMENT','NO PAYMENT'),('DUPLICATE','DUPLICATE')])
    processing_fee = IntegerField('Processing Fee')
    space_fee = FloatField('Space Fee')
    merchant_fee = FloatField('Merchant Fee')
    rider_fee = IntegerField('Rider Fee')
    paypal_donation = IntegerField('PayPal Donation')
    invoice_date = DateField('Invoice Date', validators=[RequiredIf('invoice_number')])
    notes = TextAreaField('Notes')
    submit = SubmitField('Update Invoice')

class SendInvoiceForm(FlaskForm):
    invoice_amount = FloatField('Invoice Amount')
    space_fee = FloatField('Space Fee')
    processing_fee = IntegerField('Processing Fee')
    merchant_fee = FloatField('Total Invoice Amount')
    rider_fee = IntegerField('Rider Fee')
    registration_amount = IntegerField('Registration Amount')
    invoice_number = IntegerField('Invoice Number', validators=[Optional()])
    invoice_email = StringField('Invoice Email')
    paypal_donation = IntegerField('PayPal Donation')
    nmr_amount = IntegerField('NMR Amount')
    invoice_date = DateField('Invoice Date', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Send Invoice with PayPal')

class PayInvoiceForm(FlaskForm):
    invoice_amount = FloatField('Invoice Amount', validators=[DataRequired()])
    registration_amount = IntegerField('Registration Amount', validators=[Optional()])
    processing_fee = IntegerField('Processing Fee', validators=[Optional()])
    merchant_fee = FloatField('Merchant Fee', validators=[Optional()])
    rider_fee = IntegerField('Rider Fee', validators=[Optional()])
    space_fee = FloatField('Space Fee', validators=[Optional()])
    invoice_email = StringField('Invoice Email', validators=[DataRequired()])
    invoice_number = IntegerField('Invoice Number', validators=[DataRequired()])
    invoice_status = SelectField('Invoice Status', choices=[('UNSENT','UNSENT'),('OPEN','OPEN'),('PAID','PAID'),('NO PAYMENT','NO PAYMENT'),('DUPLICATE','DUPLICATE')])
    paypal_donation = IntegerField('PayPal Donation', validators=[Optional()])
    invoice_date = DateField('Invoice Date', validators=[RequiredIf('invoice_number')])
    payment_date = DateField('Payment Date', validators=[DataRequired()])
    payment_amount = FloatField('Payment Amount', validators=[DataRequired()])
    payment_type = SelectField('Payment Type',choices=[('PAYPAL','PAYPAL'),('CHECK','CHECK')])
    check_num = IntegerField('Check Number', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Create Manual Payment')

class PayRegistrationForm(FlaskForm):
    total_due = IntegerField('Total Due')
    payment_type = SelectField('Payment Type', choices=[('ZETTLE','ZETTLE'),('CASH','CASH'),('TRAVELLER CHEQUE','TRAVELLER CHEQUE')])
    submit = SubmitField('Submit Payment')

class UpdatePayPalDonationForm(FlaskForm):
    paypal_donation = BooleanField('PayPal Donation', validators=[])
    paypal_donation_amount = IntegerField("PayPal Donation Amount", default=5, validators=[NumberRange(1,None, message=' If you would like to DONATE you must enter a value above 0')])
    submit = SubmitField('Update PayPal Donation')

class SearchInvoiceForm(FlaskForm):
    invoice_number = StringField('Invoice Number')
    email = StringField('Email')
    fname = StringField('First Name')
    lname = StringField('Last name')
    submit = SubmitField('Search')

class WaiverForm(FlaskForm):
    
    paypal_donation = BooleanField('Please check here if you would like to DONATE to cover your Paypal processing fees.', validators=[])
    paypal_donation_amount = IntegerField("PayPal Donation Amount", default=5, validators=[NumberRange(1,None, message=' If you would like to DONATE you must enter a value above 0')])

    signature = HiddenField('signature',render_kw={'id':'signature'})
    
    submit = SubmitField('Submit',render_kw={'id':'submit','data_action':'save-svg'})

class PaymentForm(FlaskForm):
    type = SelectField('Payment Type', validators=[DataRequired()], choices=[('ZETTLE','ZETTLE'),('CASH','CASH'),('TRAVELLER CHEQUE','TRAVELLER CHEQUE'),('PAYPAL','PAYPAL'),('CHECK','CHECK')])
    check_num = IntegerField('Check Number', validators=[Optional()])
    payment_date = DateTimeField('Payment Date', validators=[DataRequired()])
    registration_amount = IntegerField('Registration Amount', default=0, validators=[NumberRange(0,None, message='Value must be 0 or greater')])
    nmr_amount = IntegerField('NMR Amount', default=0, validators=[NumberRange(0,None, message='Value must be 0 or greater')])
    paypal_donation_amount = IntegerField('PayPal Donation Amount', validators=[NumberRange(0,None, message='Value must be 0 or greater')])
    space_fee_amount = FloatField('Space Fee', default=0.0, validators=[NumberRange(0,None, message='Value must be 0 or greater')])
    processing_fee_amount = IntegerField('Processing Fee', default=0, validators=[NumberRange(0,None, message='Value must be 0 or greater')])
    rider_fee_amount = IntegerField('Rider Fee', default=0, validators=[NumberRange(0,None, message='Value must be 0 or greater')])
    electricity_fee_amount = FloatField('Electricity Fee', default=0.0, validators=[NumberRange(0,None, message='Value must be 0 or greater')])
    amount = FloatField('Total Payment', default=0.0, validators=[NumberRange(0,None, message='Value must be 0 or greater')])
    invoice_number  = IntegerField('Invoice Number', validators=[Optional()])
    submit = SubmitField('Update Payment')

class ReportForm(FlaskForm):
    report_type = SelectField('Report Type', validators=[DataRequired()], choices=reporttypedata)
    dt_start = DateField('Start Date', format='%Y-%m-%d')
    dt_end = DateField('End Date', format='%Y-%m-%d')
    submit = SubmitField('Submit')

class BowForm(FlaskForm):
    id = IntegerField("Bow Id")
    poundage = DecimalField('Poundage')
    submit = SubmitField('Submit')

class MarshalForm(FlaskForm):
    regid = IntegerField()
    chivalric_inspection = BooleanField('Heavy Spear Inspection')
    rapier_inspection = BooleanField('Rapier Inspection')
    chivalric_spear_inspection = BooleanField('Heavy Spear Inspection')
    rapier_spear_inspection = BooleanField('Rapier Inspection')
    combat_archery_inspection = BooleanField('Combat Archery Inspection')
    bows = FieldList(FormField(BowForm))
    crossbows = FieldList(FormField(BowForm))
    submit = SubmitField('Submit')

class IncidentForm(FlaskForm):
    incident_date = DateTimeLocalField('Incident Date/Time', default=datetime.today)
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit Incident')

class LodgingForm(FlaskForm):
    name = StringField('Lodging Name', validators=[DataRequired()])
    # event = SelectField('Event', validators=[DataRequired()])
    submit = SubmitField('Create Lodging')

class KingdomForm(FlaskForm):
    name = StringField('Kingdom Name', validators=[DataRequired()])
    submit = SubmitField('Create Lodging')  

class StandardUploadForm(FlaskForm):
    file = FileField('Upload File', validators=[DataRequired()])
    # event = SelectField('Event', validators=[DataRequired()])
    submit = SubmitField('Submit Upload')

class MerchantForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired()])
    sca_name = StringField('SCA Name', validators=[Optional()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    text_permission = BooleanField('Permission to Text', default=False, validators=[Optional()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state_province = StringField('State/Province', validators=[DataRequired()])
    zip = IntegerField('Zip Code', validators=[DataRequired()])
    frontage_width = IntegerField('Frontage Width (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    frontage_depth = IntegerField('Frontage Depth (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    ropes_front = IntegerField('Ropes Front (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    ropes_back = IntegerField('Ropes Back (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    ropes_left = IntegerField('Ropes Left (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    ropes_right = IntegerField('Ropes Right (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    additional_space_information = TextAreaField('Additional Space Information', validators=[Optional()])
    electricity_request = TextAreaField('Electricity Request', validators=[Optional()])
    food_merchant_agreement = BooleanField('FOOD MERCHANTS: I agree to send menu and pricing to merchancrat@gulfwars.org along with a copy of your food safety certification.', validators=[Optional()]) 
    estimated_date_of_arrival = SelectField('Estimated Date of Arrival', validators=[NoneOf('-', message='You must select an Arrival Date')])
    service_animal = BooleanField('Service Animal', default=False, validators=[Optional()])
    last_3_years = BooleanField('Have you been a merchant at Gulf Wars in the last 3 years?', default=False, validators=[Optional()])
    require_merchant_parking = BooleanField('Will you require merchant parking?', default=False)
    vehicle_length = IntegerField('Vehicle Length (in feet)', validators=[RequiredIf('require_merchant_parking')])
    vehicle_license_plate = StringField('Vehicle License Plate', validators=[RequiredIf('require_merchant_parking')])
    vehicle_state = StringField('Vehicle State', validators=[RequiredIf('require_merchant_parking')])
    trailer_length = IntegerField('Trailer Length (in feet)', validators=[Optional()])  
    trailer_license_plate = StringField('Trailer License Plate', validators=[Optional()])
    trailer_state = StringField('Trailer State', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    signature = StringField('By Typing your name here, you are signing this application electronically. You agree your electronic signature is the legal equivalent of your manual signature on this application.', validators=[DataRequired()])
    submit = SubmitField('Submit Merchant Application',render_kw={'id':'submit'})

class EditMerchantForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired()])
    status = SelectField('Merchant Status', choices=[('PENDING','PENDING'),('APPROVED','APPROVED'),('DENIED','DENIED'),('WAITLIST','WAITLIST'),('DUPLICATE','DUPLICATE')], validators=[DataRequired()])
    sca_name = StringField('SCA Name', validators=[DataRequired()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    text_permission = BooleanField('Permission to Text', default=False, validators=[Optional()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state_province = StringField('State/Province', validators=[DataRequired()])
    zip = IntegerField('Zip Code', validators=[DataRequired()])
    frontage_width = IntegerField('Frontage Width (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    frontage_depth = IntegerField('Frontage Depth (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    ropes_front = IntegerField('Ropes Front (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    ropes_back = IntegerField('Ropes Back (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    ropes_left = IntegerField('Ropes Left (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    ropes_right = IntegerField('Ropes Right (in feet)', validators=[NumberRange(0,None, message='Value must be 0 or greater')], default=0)
    space_fee = FloatField('Space Fee', default=0)
    additional_space_information = TextAreaField('Additional Space Information', validators=[Optional()])
    processing_fee = IntegerField('Processing Fee',validators=[DataRequired()], default=0)
    merchant_fee = FloatField('Merchant Fee',validators=[DataRequired()], default=0)
    electricity_request = TextAreaField('Electricity Request', validators=[Optional()])
    food_merchant_agreement = BooleanField('FOOD MERCHANTS: Agreement to send menu and pricing', validators=[Optional()]) 
    estimated_date_of_arrival = SelectField('Estimated Date of Arrival', validators=[NoneOf('-', message='You must select an Arrival Date')])
    service_animal = BooleanField('Service Animal', default=False, validators=[Optional()])
    last_3_years = BooleanField('Have you been a merchant at Gulf Wars in the last 3 years?', default=False, validators=[Optional()])
    vehicle_length = IntegerField('Vehicle Length (in feet)', validators=[Optional()])
    vehicle_license_plate = StringField('Vehicle License Plate', validators=[Optional()])
    vehicle_state = StringField('Vehicle State', validators=[Optional()])
    trailer_length = IntegerField('Trailer Length (in feet)', validators=[Optional()])  
    trailer_license_plate = StringField('Trailer License Plate', validators=[Optional()])
    trailer_state = StringField('Trailer State', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    application_date = DateTimeField('Application Date', validators=[DataRequired()])
    signature = StringField('Signature', validators=[DataRequired()])
    
    submit = SubmitField(
        'Update Merchant Application',
        render_kw={'id':'submit','data_action':'save-svg'}
    )

class MerchantCheckinForm(FlaskForm):

    notes = TextAreaField('Notes', validators=[Optional()])
    space_fee = FloatField('Space Fee')
    
    submit = SubmitField(
        'Checkin Merchant',
        render_kw={'id':'submit','data_action':'save-svg'}
    )

class MerchantUpdateFeesForm(FlaskForm):

    electricity_request = TextAreaField('Electricity Request', validators=[Optional()])
    electricity_fee = FloatField('Electricity Fee', validators=[DataRequired()])
    electricity_balance = FloatField('Electricity Fee Balance', validators=[DataRequired()])
    space_fee = FloatField('Space Fee', validators=[DataRequired()])
    space_fee_balance = FloatField('Space Fee Balance', validators=[DataRequired()])
    processing_fee = IntegerField('Processing Fee', validators=[DataRequired()])
    processing_fee_balance = IntegerField('Processing Fee Balance', validators=[DataRequired()])
    frontage_width = IntegerField('Frontage Width (in feet)', validators=[DataRequired()])
    frontage_depth = IntegerField('Frontage Depth (in feet)', validators=[DataRequired()])
    ropes_front = IntegerField('Ropes Front (in feet)', default=0)
    ropes_back = IntegerField('Ropes Back (in feet)', default=0)
    ropes_left = IntegerField('Ropes Left (in feet)', default=0)
    ropes_right = IntegerField('Ropes Right (in feet)', default=0)
    
    submit = SubmitField('Update Fees')

class EventVariablesForm(FlaskForm):

    name = StringField('Event Name', validators=[DataRequired()])
    year = IntegerField('Event Year', validators=[DataRequired()])
    event_title = StringField('Event Title', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    location = StringField('Event Location', validators=[DataRequired()])
    description = TextAreaField('Event Description', validators=[DataRequired()])
    preregistration_open_date = DateField('Preregistration Open Date', format='%Y-%m-%d', validators=[DataRequired()])
    preregistration_close_date = DateField('Preregistration Close Date', format='%Y-%m-%d', validators=[DataRequired()])
    autocrat1 = StringField('Autocrat 1', validators=[])
    autocrat2 = StringField('Autocrat 2', validators=[])
    autocrat3 = StringField('Autocrat 3', validators=[])
    reservationist = StringField('Reservationist', validators=[])
    merchant_application_deadline = DateField('Merchant Application Deadline', format='%Y-%m-%d', validators=[DataRequired()])
    merchantcrat_email = StringField('Merchantcrat Email', validators=[DataRequired(), Email()])
    marchantcrat_phone = StringField('Merchantcrat Phone', validators=[DataRequired()])
    merchant_preregistration_open_date = DateField('Merchant Preregistration Open Date', format='%Y-%m-%d', validators=[DataRequired()])
    merchant_preregistration_close_date = DateField('Merchant Preregistration Close Date', format='%Y-%m-%d', validators=[DataRequired()])
    merchant_processing_fee = IntegerField('Merchant Processing Fee', validators=[DataRequired()])
    merchant_late_processing_fee = IntegerField('Merchant Late Processing Fee', validators=[DataRequired()])
    merchant_squarefoot_fee = FloatField('Merchant Square Foot Fee', validators=[DataRequired()])
    merchant_bounced_check_fee = FloatField('Merchant Bounced Check Fee', validators=[DataRequired()])

    submit = SubmitField('Update Event Variables')

class PriceSheetForm(FlaskForm):
    arrival_date = SelectField('Arrival Date', validators=[DataRequired()])
    prereg_price = IntegerField('Pre-Reg Price', validators=[DataRequired()])
    atd_price = IntegerField('ATD Price', validators=[DataRequired()])
    submit = SubmitField('Submit Price Change')

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired()])
    description = TextAreaField('Department Description', validators=[])
    submit = SubmitField('Create Department')

class TopicForm(FlaskForm):
    topic_name = StringField('Name Topic', validators=[DataRequired()])

class TagForm(FlaskForm):
    tag_name = StringField('New Tag', validators=[DataRequired()])

class ScheduledEventForm(FlaskForm):
    name = StringField('Scheduled Event Name', validators=[DataRequired()])
    start_datetime = DateTimeLocalField('Event Date/Time', validators=[DataRequired()])
    end_datetime = DateTimeLocalField('Event Date/Time', validators=[DataRequired()])
    instructor = StringField('Instructor', validators=[DataRequired()])
    short_description = TextAreaField('Short Description', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    topic = SelectField('Topic', validators=[])
    new_topic = FieldList(FormField(TopicForm), min_entries=0, max_entries=1)
    tags = SelectMultipleField('Tags',validators=[])
    new_tag = FieldList(FormField(TagForm), min_entries=0, max_entries=10)
    user_instructor = SelectField('User Instructor',validators=[Optional()])
    submit = SubmitField('Create Scheduled Event')

    def populate_object(self, obj):
        # Name
        if self.name.data:
            obj.name = self.name.data.strip()
        # Start Date/Time
        if self.start_datetime.data:
            obj.start_datetime = self.start_datetime.data
        # End Date/Time
        if self.end_datetime.data:
            obj.end_datetime = self.end_datetime.data
        # Instructor
        if self.instructor.data:
            obj.instructor = self.instructor.data.strip()
        # Short Description
        if self.short_description.data:
            obj.short_description = self.short_description.data
        # Description
        if self.description.data:
            obj.description = self.description.data
        # Location
        if self.location.data:
            obj.location = self.location.data.strip()        
        # Topic
        if self.topic.data and self.topic.data != '-':
            obj.topic_id = self.topic.data      
        # Tags - Iterate
        obj.tags = []
        for tagid in self.tags.data:
            if tagid != '-':
                obj.tags.append(get_tag(tagid))
        # User Instructor
        if self.user_instructor.data and self.user_instructor.data != '-':
            obj.user_instructor_id = self.user_instructor.data    

    def populate_form(self, obj):
        # Name
        if obj.name:
            self.name.data = obj.name
        # Start Date/Time
        if obj.start_datetime:
            self.start_datetime.data = obj.start_datetime
        # End Date/Time
        if obj.end_datetime:
            self.end_datetime.data = obj.end_datetime
        # Instructor
        if obj.instructor:
            self.instructor.data = obj.instructor
        # Short Description
        if obj.short_description:
            self.short_description.data = obj.short_description
        # Description
        if obj.description:
            self.description.data = obj.description
        # Location
        if obj.location:
            self.location.data = obj.location     
        # Topic
        if obj.topic_id:
            self.topic.data = str(obj.topic_id)        
        # Tags - Iterate
        for tag in obj.tags:
            self.tags.data.append(str(tag.id))
        # User Instructor
        if obj.user_instructor_id:
            self.self.user_instructor.data = obj.user_instructor_id

class PayPalForm(FlaskForm):
    base_url = StringField('Base URL', validators=[DataRequired()])
    client_id = StringField('Client ID', validators=[DataRequired()])
    client_secret = StringField('Client Secret', validators=[DataRequired()])
    webhook_id = StringField('Webhook ID', validators=[DataRequired()])
    submit = SubmitField('Update PayPal Info')