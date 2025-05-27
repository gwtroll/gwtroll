from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, HiddenField, SelectMultipleField, TextAreaField, DecimalField, FieldList, FormField, DateTimeField, FileField
from wtforms.fields import DateField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, InputRequired, Optional, ValidationError, NoneOf, EqualTo, Length
import pandas as pd
import datetime

kingdom_df = pd.read_csv('gwkingdoms.csv')
kingdomdata = kingdom_df.to_dict(orient='list')

agedata = [('18+', 'Adult 18+'), ('13-17', 'Teen 13 - 17'), ('6-12', 'Youth 6 - 12'), ('0-5', 'Child 0 - 5'),('Royals','Royals')]

mbrdata = [('Member', 'Member'), ('Non-Member', 'Non-Member')]

reporttypedata = [('royal_registrations', 'royal_registrations'), ('land_pre-reg', 'land_pre-reg'), ('full_export', 'full_export'), ('full_signatue_export', 'full_signature_export'), ('full_checkin_report', 'full_checkin_report'), ('at_door_count', 'at_door_count'), ('kingdom_count', 'kingdom_count'), ('ghost_report', 'ghost_report'), ('earlyon','early_on_report'), ('paypal_paid_export','paypal_paid_export'),('paypal_canceled_export','paypal_canceled_export'),('paypal_recon_export','paypal_recon_export'),('atd_export','atd_export'),('log_export','log_export'),('minor_waivers','minor_waivers')]

arrivaldata = [('03-08-2025','Saturday - March 8th 2025'),('03-09-2025','Sunday - March 9th 2025'),('03-10-2025','Monday - March 10th 2025'),('03-11-2025','Tuesday - March 11th 2025'),('03-12-2025','Wednesday - March 12th 2025'),('03-13-2025','Tursday - March 13th 2025'),('03-14-2025','Friday - March 14th 2025'),('03-15-2025','Saturday - March 15th 2025'),('Early_On','Early On')]

paymentdata = [('',''),('cash','Cash'), ('zettle','Zettle'),('travlers_check','Travlers Check')]

preregstatusdata = [('',''),('SUCCEEDED','SUCCEEDED')]

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
    role = SelectMultipleField('Role', validators=[DataRequired()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    event = SelectField('Event', validators=[])
    medallion = IntegerField('Medallion')
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreateRoleForm(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired()])
    role_name = StringField('Role Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreateEventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_year = IntegerField('Event Year', validators=[DataRequired()])
    event_description = TextAreaField('Event Description', validators=[DataRequired()])
    event_start = DateField('Event Start', format='%Y-%m-%d', validators=[DataRequired()])
    event_end = DateField('Event End', format='%Y-%m-%d', validators=[DataRequired()])
    event_location = StringField('Event Location', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditUserForm(FlaskForm):
    id = StringField('User Id', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    role = SelectMultipleField('Role', validators=[DataRequired()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    event = SelectField('Event', validators=[])
    medallion = IntegerField('Medallion')
    active = BooleanField('Active')
    submit = SubmitField('Submit')

class UpdatePasswordForm(FlaskForm):
    id = StringField('User Id', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords Must Match'), Length(min=6, max=32, message='Minimum Password Length  of 6 Characters')])
    confirm = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords Must Match')])
    submit = SubmitField('Submit')

class CreateRegForm(FlaskForm):
    #regid = HiddenField(None)
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    scaname = StringField('SCA Name', validators=[])
    kingdom = SelectField('Kingdom', validators=[DataRequired()], choices=kingdomdata)
    lodging = SelectField('Camping Group', validators=[DataRequired()])
    age = SelectField('Age Range', validators=[DataRequired()], choices=agedata)
    mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    mbr_num = IntegerField('Membership #', validators=[RequiredIfMembership('mbr')])
    mbr_num_exp = DateField('Exp Date', validators=[RequiredIfMembership('mbr')])
    city = StringField('City')
    state_province = StringField('State/Province')
    zip = IntegerField('Zip', validators=[Optional()])
    country = StringField('Country')
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email')
    invoice_email = StringField('Invoice Email')
    emergency_contact_name = StringField('Legal Name', validators=[DataRequired()])
    emergency_contact_phone = StringField('Phone', validators=[DataRequired()])
    #mbr_num
    #mbr_exp
    submit = SubmitField('Submit')

class CreatePreRegForm(FlaskForm):
    #regid = HiddenField(None)
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    scaname = StringField('SCA Name', validators=[])
    city = StringField('City', validators=[DataRequired()])
    state_province = StringField('State/Province', validators=[DataRequired()])
    zip = IntegerField('Zip', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),Email()])
    invoice_email = StringField('Invoice Email', validators=[DataRequired(),Email()])
    kingdom = SelectField('Kingdom', validators=[NoneOf('-', message='You must select a Kingdom')], choices=kingdomdata)
    lodging = SelectField('Camping Group', validators=[NoneOf('-', message='You must select a Lodging')])
    emergency_contact_name = StringField('Legal Name', validators=[DataRequired()])
    emergency_contact_phone = StringField('Phone', validators=[DataRequired()])
    age = SelectField('Age Range', validators=[DataRequired()], id='age', choices=agedata)
    mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    mbr_num = IntegerField('Membership #', validators=[RequiredIfMembership('mbr')])
    mbr_num_exp = DateField('Exp Date', validators=[RequiredIfMembership('mbr')])
    expected_arrival_date = SelectField('Arrival Date', validators=[DataRequired()], choices=arrivaldata)
    paypal_donation = BooleanField('Please check here if you would like to donate $3 to cover your Paypal processing fees.', validators=[])
    royal_departure_date = DateField('Departure Date', validators=[Optional()])
    royal_title = StringField('Royal Title', validators=[Optional()])

    submit = SubmitField('Register')

class CheckinForm(FlaskForm):
    regid = IntegerField()
    fname = StringField('First Name')
    lname = StringField('Last Name')
    scaname = StringField('SCA Name')
    kingdom = SelectField('Kingdom', validators=[DataRequired()], choices=kingdomdata)
    lodging = SelectField('Camping Group', validators=[DataRequired()])
    age = SelectField('Age Range', validators=[DataRequired()], choices=agedata)
    mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    mbr_num = IntegerField('Membership Number')
    mbr_num_exp = DateField('Membership Expiration Date')
    medallion = IntegerField('Medallion #', validators=[DataRequired()])
    minor_waiver = SelectField('Minor Waiver', validators=[NoneOf('-', message='You must select a Minor Form Validation')], choices=[('-','-'),('Signed by Parent/Guardian','Signed by Parent/Guardian'),('Medical Authorization Form Submitted','Medical Authorization Form Submitted')])
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit')

class EditForm(FlaskForm):
    regid = IntegerField()
    fname = StringField('First Name')
    lname = StringField('Last Name')
    scaname = StringField('SCA Name')
    city = StringField('City')
    state_province = StringField('State/Province')
    zip = IntegerField('Zip Code')
    country = StringField('Country')
    phone = StringField('Phone')
    email = StringField('Communication Email')
    invoice_email = StringField('Invoice Email')
    kingdom = SelectField('Kingdom', validators=[DataRequired()], choices=kingdomdata)
    lodging = SelectField('Camping Group', validators=[DataRequired()])
    expected_arrival_date = DateField("Arrival Date")
    age = SelectField('Age Range', validators=[DataRequired()], choices=agedata)
    mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    medallion = IntegerField('Medallion #', validators=[DataRequired()])
    total_due = IntegerField('Total Due')
    paypal_donation = IntegerField('PayPal Donation')
    prereg = BooleanField('PreReg')
    early_on = BooleanField('Early On')
    mbr_num = IntegerField('Member Number')
    mbr_num_exp = DateField('Member Exp Date')
    emergency_contact_name = StringField('Name')
    emergency_contact_phone = StringField('Phone')
    notes = TextAreaField('Notes')

    #mbr_exp
    submit = SubmitField('Submit')

class UpdateInvoiceForm(FlaskForm):
    invoice_amount = IntegerField('Invoice Amount')
    registration_amount = IntegerField('Registration Amount')
    invoice_email = StringField('Invoice Email')
    invoice_number = IntegerField('Invoice Number', validators=[])
    invoice_status = SelectField('Invoice Status', choices=[('UNSENT','UNSENT'),('OPEN','OPEN'),('PAID','PAID'),('NO PAYMNET','NO PAYMENT'),('DUPLICATE','DUPLICATE')])
    paypal_donation = IntegerField('PayPal Donation')
    invoice_date = DateField('Invoice Date', validators=[RequiredIf('invoice_number')])
    payment_date = DateField('Payment Date')
    payment_amount = IntegerField('Payment Amount')
    payment_type = SelectField('Payment Type',choices=[('PAYPAL','PAYPAL'),('CHECK','CHECK')])
    check_num = IntegerField('Check Number')
    notes = TextAreaField('Notes')
    submit = SubmitField('Update Invoice')

class SendInvoiceForm(FlaskForm):
    invoice_amount = IntegerField('Invoice Amount')
    registration_amount = IntegerField('Registration Amount')
    invoice_number = IntegerField('Invoice Number', validators=[])
    invoice_email = StringField('Invoice Email')
    paypal_donation = IntegerField('PayPal Donation')
    invoice_date = DateField('Invoice Date', validators=[RequiredIf('invoice_number')])
    notes = TextAreaField('Notes')
    submit = SubmitField('Create Invoice')

class PayInvoiceForm(FlaskForm):
    invoice_amount = IntegerField('Invoice Amount')
    registration_amount = IntegerField('Registration Amount')
    invoice_email = StringField('Invoice Email')
    invoice_number = IntegerField('Invoice Number', validators=[])
    invoice_status = SelectField('Invoice Status', choices=[('UNSENT','UNSENT'),('OPEN','OPEN'),('PAID','PAID'),('NO PAYMNET','NO PAYMENT'),('DUPLICATE','DUPLICATE')])
    paypal_donation = IntegerField('PayPal Donation')
    invoice_date = DateField('Invoice Date', validators=[RequiredIf('invoice_number')])
    payment_date = DateField('Payment Date')
    payment_amount = IntegerField('Payment Amount')
    payment_type = SelectField('Payment Type',choices=[('PAYPAL','PAYPAL'),('CHECK','CHECK')])
    check_num = IntegerField('Check Number')
    notes = TextAreaField('Notes')
    submit = SubmitField('Update Invoice')

class PayRegistrationForm(FlaskForm):
    total_due = IntegerField('Total Due')
    payment_type = SelectField('Payment Type', choices=[('ZETTLE','ZETTLE'),('CASH','CASH'),('TRAVELLER CHEQUE','TRAVELLER CHEQUE')])
    submit = SubmitField('Submit')

class SearchInvoiceForm(FlaskForm):
    invoice_number = StringField('Invoice Number')
    email = StringField('Email')
    fname = StringField('First Name')
    lname = StringField('Last name')
    submit = SubmitField('Search')

class WaiverForm(FlaskForm):
    
    paypal_donation = BooleanField('Please check here if you would like to donate $3 to cover payment processing fees.',
                                   render_kw={'id':'test'})

    signature = HiddenField(
        'signature',
        render_kw={'id':'signature'}
    )
    
    submit = SubmitField(
        'Submit',
        render_kw={'id':'submit','data_action':'save-svg'}
    )

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
    incident_date = DateTimeLocalField('Incident Date/Time', default=datetime.datetime.today)
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit Incident')

class LodgingForm(FlaskForm):
    name = StringField('Lodging Name', validators=[DataRequired()])
    event = SelectField('Event', validators=[DataRequired()])
    submit = SubmitField('Create Lodging')

class StandardUploadForm(FlaskForm):
    file = FileField('Upload File', validators=[DataRequired()])
    event = SelectField('Event', validators=[DataRequired()])
    submit = SubmitField('Submit Upload')