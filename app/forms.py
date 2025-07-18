from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, HiddenField, SelectMultipleField, TextAreaField, DecimalField, FieldList, FormField, DateTimeField, FileField, FloatField
from wtforms.fields import DateField, DateTimeLocalField, DateTimeField
from wtforms.validators import DataRequired, Email, InputRequired, Optional, ValidationError, NoneOf, EqualTo, Length
import pandas as pd
import datetime

agedata = [('18+', 'Adult 18+'), ('13-17', 'Teen 13 - 17'), ('6-12', 'Youth 6 - 12'), ('0-5', 'Child 0 - 5'),('Royals','Royals')]

mbrdata = [('Member', 'Member'), ('Non-Member', 'Non-Member')]

reporttypedata = [('royal_registrations', 'royal_registrations'), ('land_pre-reg', 'land_pre-reg'), ('full_export', 'full_export'), ('full_signatue_export', 'full_signature_export'), ('full_checkin_report', 'full_checkin_report'), ('at_door_count', 'at_door_count'), ('kingdom_count', 'kingdom_count'), ('ghost_report', 'ghost_report'), ('earlyon','early_on_report'), ('paypal_paid_export','paypal_paid_export'),('paypal_canceled_export','paypal_canceled_export'),('paypal_recon_export','paypal_recon_export'),('atd_export','atd_export'),('log_export','log_export'),('minor_waivers','minor_waivers')]

# arrivaldata = [('03-08-2025','Saturday - March 8th 2025'),('03-09-2025','Sunday - March 9th 2025'),('03-10-2025','Monday - March 10th 2025'),('03-11-2025','Tuesday - March 11th 2025'),('03-12-2025','Wednesday - March 12th 2025'),('03-13-2025','Tursday - March 13th 2025'),('03-14-2025','Friday - March 14th 2025'),('03-15-2025','Saturday - March 15th 2025'),('Early_On','Early On')]

# merchant_arrivaldata = [('03-07-2025','Friday - March 7th 2025'),('03-08-2025','Saturday - March 8th 2025'),('03-09-2025','Sunday - March 9th 2025'),('03-10-2025','Monday - March 10th 2025'),('03-11-2025','Tuesday - March 11th 2025'),('03-12-2025','Wednesday - March 12th 2025'),('03-13-2025','Tursday - March 13th 2025'),('03-14-2025','Friday - March 14th 2025'),('03-15-2025','Saturday - March 15th 2025')]

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
    department = SelectField('Department', validators=[DataRequired()], choices=[])
    # event = SelectField('Event', validators=[])
    medallion = IntegerField('Medallion')
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreateRoleForm(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired()])
    role_name = StringField('Role Name', validators=[DataRequired()])
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
    id = StringField('User Id', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    role = SelectMultipleField('Role', validators=[DataRequired()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    department = SelectField('Department', validators=[DataRequired()], choices=[])
    # event = SelectField('Event', validators=[])
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
    kingdom = SelectField('Kingdom', validators=[DataRequired()])
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
    kingdom = SelectField('Kingdom', validators=[NoneOf('-', message='You must select a Kingdom')])
    lodging = SelectField('Camping Group', validators=[NoneOf('-', message='You must select a Lodging')])
    emergency_contact_name = StringField('Legal Name', validators=[DataRequired()])
    emergency_contact_phone = StringField('Phone', validators=[DataRequired()])
    age = SelectField('Age Range', validators=[DataRequired()], id='age', choices=agedata)
    mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    mbr_num = IntegerField('Membership #', validators=[RequiredIfMembership('mbr')])
    mbr_num_exp = DateField('Exp Date', validators=[RequiredIfMembership('mbr')])
    expected_arrival_date = SelectField('Arrival Date', validators=[DataRequired()])
    paypal_donation = BooleanField('Please check here if you would like to donate $3 to cover your Paypal processing fees.', validators=[])
    royal_departure_date = DateField('Departure Date', validators=[Optional()])
    royal_title = StringField('Royal Title', validators=[Optional()])

    submit = SubmitField('Register')

class CheckinForm(FlaskForm):
    regid = IntegerField()
    fname = StringField('First Name')
    lname = StringField('Last Name')
    scaname = StringField('SCA Name')
    kingdom = SelectField('Kingdom', validators=[DataRequired()])
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
    country = StringField('Country', default='United States')
    phone = StringField('Phone')
    email = StringField('Communication Email')
    invoice_email = StringField('Invoice Email')
    age = SelectField('Age Range', validators=[DataRequired()], choices=agedata)
    emergency_contact_name = StringField('Name')
    emergency_contact_phone = StringField('Phone')
    mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    mbr_num = IntegerField('Member Number')
    mbr_num_exp = DateField('Member Exp Date')
    
    reg_date_time = DateTimeField('Registration Date/Time')
    prereg = BooleanField('PreReg')
    prereg_date_time = DateTimeField('PreReg Date/Time')
    expected_arrival_date = DateField("Arrival Date")
    early_on = BooleanField('Early On')
    notes = TextAreaField('Notes')
    duplicate = BooleanField('Duplicate Registration')

    registration_price = IntegerField('Registration Price', validators=[DataRequired()])
    registration_balance = IntegerField('Registration Balance', validators=[DataRequired()])
    nmr_price = IntegerField('NMR Price', validators=[DataRequired()])
    nmr_balance = IntegerField('NMR Balance', validators=[DataRequired()])
    paypal_donation = IntegerField('PayPal Donation', validators=[DataRequired()])
    paypal_donation_balance = IntegerField('PayPal Donation Balance', validators=[DataRequired()])
    nmr_donation = IntegerField('NMR Donation', validators=[DataRequired()])
    total_due = IntegerField('Total Due', validators=[DataRequired()])
    balance = IntegerField('Balance', validators=[DataRequired()])

    minor_waiver = StringField('Minor Waiver', validators=[NoneOf('-', message='You must select a Minor Form Validation')])
    checkin = DateTimeField('Checkin Date/Time')
    medallion = IntegerField('Medallion #', validators=[DataRequired()])
    actual_arrival_date = DateField('Actual Arrival Date')

    kingdom = SelectField('Kingdom', validators=[DataRequired()])
    lodging = SelectField('Camping Group', validators=[DataRequired()])

    #mbr_exp
    submit = SubmitField('Submit')

class RiderForm(Form):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    scaname = StringField('SCA Name', validators=[DataRequired()])
    minor = BooleanField('Minor', default=False, validators=[Optional()])
    regid = IntegerField('Registration Id', validators=[DataRequired()])
    submit = SubmitField('Add Rider')

class EarlyOnForm(FlaskForm):
    
    arrival_date = SelectField('Estimated Date of Arrival', validators=[DataRequired()])
    department = SelectField('Department', validators=[DataRequired()], choices=[])
    notes = TextAreaField('Notes')
    riders = FieldList(FormField(RiderForm), min_entries=0, max_entries=10)
    submit = SubmitField('Submit Early On Request')

class EarlyOnApprovalForm(FlaskForm):
    arrival_date = SelectField('Estimated Date of Arrival', validators=[DataRequired()])
    department = SelectField('Department', validators=[DataRequired()], choices=[])
    notes = TextAreaField('Notes')
    riders = FieldList(FormField(RiderForm), min_entries=0, max_entries=10)
    dept_approval_status = SelectField('Department Approval', choices=[('PENDING','PENDING'),('APPROVED','APPROVED'),('DENIED','DENIED')])
    autocrat_approval_status = SelectField('Autocrat Approval', choices=[('PENDING','PENDING'),('APPROVED','APPROVED'),('DENIED','DENIED')])
    submit = SubmitField('Submit Early On Request')

class UpdateInvoiceForm(FlaskForm):
    invoice_amount = IntegerField('Invoice Amount')
    registration_amount = IntegerField('Registration Amount')
    invoice_email = StringField('Invoice Email')
    invoice_number = IntegerField('Invoice Number', validators=[])
    invoice_status = SelectField('Invoice Status', choices=[('UNSENT','UNSENT'),('OPEN','OPEN'),('PAID','PAID'),('NO PAYMNET','NO PAYMENT'),('DUPLICATE','DUPLICATE')])
    processing_fee = IntegerField('Processing Fee')
    space_fee = FloatField('Space Fee')
    merchant_fee = FloatField('Merchant Fee')
    rider_fee = IntegerField('Rider Fee')
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
    space_fee = FloatField('Space Fee')
    processing_fee = IntegerField('Processing Fee')
    merchant_fee = FloatField('Merchant Fee')
    rider_fee = IntegerField('Rider Fee')
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
    processing_fee = IntegerField('Processing Fee')
    merchant_fee = FloatField('Merchant Fee')
    rider_fee = IntegerField('Rider Fee')
    space_fee = FloatField('Space Fee')
    invoice_email = StringField('Invoice Email')
    invoice_number = IntegerField('Invoice Number', validators=[])
    invoice_status = SelectField('Invoice Status', choices=[('UNSENT','UNSENT'),('OPEN','OPEN'),('PAID','PAID'),('NO PAYMNET','NO PAYMENT'),('DUPLICATE','DUPLICATE')])
    paypal_donation = IntegerField('PayPal Donation')
    invoice_date = DateField('Invoice Date', validators=[RequiredIf('invoice_number')])
    payment_date = DateField('Payment Date')
    payment_amount = FloatField('Payment Amount')
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
    frontage_width = IntegerField('Frontage Width (in feet)', validators=[DataRequired()], default=0)
    frontage_depth = IntegerField('Frontage Depth (in feet)', validators=[DataRequired()], default=0)
    ropes_front = IntegerField('Ropes Front (in feet)', default=0)
    ropes_back = IntegerField('Ropes Back (in feet)', default=0)
    ropes_left = IntegerField('Ropes Left (in feet)', default=0)
    ropes_right = IntegerField('Ropes Right (in feet)', default=0)
    additional_space_information = TextAreaField('Additional Space Information', validators=[Optional()])
    electricity_request = TextAreaField('Electricity Request', validators=[Optional()])
    food_merchant_agreement = BooleanField('FOOD MERCHANTS: I agree to send menu and pricing to merchancrat@gulfwars.org along with a copy of your food safety certification.', validators=[Optional()]) 
    estimated_date_of_arrival = SelectField('Estimated Date of Arrival', validators=[DataRequired()])
    service_animal = BooleanField('Service Animal', default=False, validators=[Optional()])
    last_3_years = BooleanField('Have you been a merchant at Gulf Wars in the last 3 years?', default=False, validators=[Optional()])
    vehicle_length = IntegerField('Vehicle Length (in feet)', validators=[Optional()])
    vehicle_license_plate = StringField('Vehicle License Plate', validators=[Optional()])
    vehicle_state = StringField('Vehicle State', validators=[Optional()])
    trailer_length = IntegerField('Trailer Length (in feet)', validators=[Optional()])  
    trailer_license_plate = StringField('Trailer License Plate', validators=[Optional()])
    trailer_state = StringField('Trailer State', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])

    signature = StringField('By Typing your name here, you are signing this application electronically. You agree your electronic signature is the legal equivalent of your manual signature on this application.', validators=[DataRequired()])
    
    submit = SubmitField(
        'Submit Merchant Application',
        render_kw={'id':'submit','data_action':'save-svg'}
    )

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
    frontage_width = IntegerField('Frontage Width (in feet)', validators=[DataRequired()])
    frontage_depth = IntegerField('Frontage Depth (in feet)', validators=[DataRequired()])
    ropes_front = IntegerField('Ropes Front (in feet)', default=0)
    ropes_back = IntegerField('Ropes Back (in feet)', default=0)
    ropes_left = IntegerField('Ropes Left (in feet)', default=0)
    ropes_right = IntegerField('Ropes Right (in feet)', default=0)
    space_fee = FloatField('Space Fee', validators=[DataRequired()])
    additional_space_information = TextAreaField('Additional Space Information', validators=[Optional()])
    processing_fee = IntegerField('Processing Fee',validators=[DataRequired()])
    merchant_fee = FloatField('Merchant Fee',validators=[DataRequired()])
    electricity_request = TextAreaField('Electricity Request', validators=[Optional()])
    food_merchant_agreement = BooleanField('FOOD MERCHANTS: Agreement to send menu and pricing', validators=[Optional()]) 
    estimated_date_of_arrival = DateField('Estimated Date of Arrival', validators=[DataRequired()])
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
    merchant_application_deadline = DateField('Merchant Application Deadline', format='%Y-%m-%d', validators=[DataRequired()])
    merchantcrat_email = StringField('Merchantcrat Email', validators=[DataRequired(), Email()])
    marchantcrat_phone = StringField('Merchantcrat Phone', validators=[DataRequired()])
    preregistration_open_date = DateField('Preregistration Open Date', format='%Y-%m-%d', validators=[DataRequired()])
    preregistration_close_date = DateField('Preregistration Close Date', format='%Y-%m-%d', validators=[DataRequired()])
    merchant_preregistration_open_date = DateField('Merchant Preregistration Open Date', format='%Y-%m-%d', validators=[DataRequired()])
    merchant_preregistration_close_date = DateField('Merchant Preregistration Close Date', format='%Y-%m-%d', validators=[DataRequired()])
    merchant_processing_fee = IntegerField('Merchant Processing Fee', validators=[DataRequired()])
    merchant_late_processing_fee = IntegerField('Merchant Late Processing Fee', validators=[DataRequired()])
    merchant_squarefoot_fee = FloatField('Merchant Square Foot Fee', validators=[DataRequired()])
    merchant_bounced_check_fee = FloatField('Merchant Bounced Check Fee', validators=[DataRequired()])

    submit = SubmitField('Update Event Variables')

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired()])
    description = TextAreaField('Department Description', validators=[])
    submit = SubmitField('Create Department')
    