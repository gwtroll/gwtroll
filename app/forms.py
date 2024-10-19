from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, HiddenField, SelectMultipleField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, InputRequired, Optional, ValidationError
import pandas as pd

lodging_df = pd.read_csv('gwlodging.csv')
lodgingdata = lodging_df.to_dict(orient='list')

kingdom_df = pd.read_csv('gwkingdoms.csv')
kingdomdata = kingdom_df.to_dict(orient='list')

agedata = [('18+', 'Adult 18+'), ('13-17', 'Teen 13 - 17'), ('6-12', 'Youth 6 - 12'), ('0-5', 'Child 0 - 5'), ('tour_adult', 'Tour 18+'), ('tour_teen', 'Tour 12 - 17'), ('tour_child', 'Tour 0 - 11')]

mbrdata = [('Member', 'Member'), ('Non-Member', 'Non-Member')]

reporttypedata = [('full_export', 'full_export'), ('full_signatue_export', 'full_signature_export'), ('full_checkin_report', 'full_checkin_report'), ('at_door_count', 'at_door_count'), ('kingdom_count', 'kingdom_count'), ('ghost_report', 'ghost_report')]

roledata = [(5, 'User'), (2, 'Shift Lead'), (1, 'Admin'), (3, 'Marshal'),(4, 'Land')]

arrivaldata = [('03-08-2024','Saturday - March 8th 2024'),('03-09-2024','Sunday - March 9th 2024'),('03-10-2024','Monday - March 10th 2024'),('03-11-2024','Tuesday - March 11th 2024'),('03-12-2024','Wednesday - March 12th 2024'),('03-13-2024','Tursday - March 13th 2024'),('03-14-2024','Friday - March 14th 2024'),('03-15-2024','Saturday - March 15th 2024')]

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
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateUserForm(FlaskForm):
    # id = StringField('User Id', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    role = SelectMultipleField('Role', validators=[DataRequired()], choices=roledata)
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditUserForm(FlaskForm):
    id = StringField('User Id', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    role = SelectMultipleField('Role', validators=[DataRequired()], choices=roledata)
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UpdatePasswordForm(FlaskForm):
    id = StringField('User Id', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreateRegForm(FlaskForm):
    #regid = HiddenField(None)
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    scaname = StringField('SCA Name', validators=[])
    kingdom = SelectField('Kingdom', validators=[DataRequired()], choices=kingdomdata)
    lodging = SelectField('Camping Group', validators=[DataRequired()], choices=lodgingdata)
    rate_age = SelectField('Age Range', validators=[DataRequired()], choices=agedata)
    rate_mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
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
    kingdom = SelectField('Kingdom', validators=[DataRequired()], choices=kingdomdata)
    lodging = SelectField('Camping Group', validators=[DataRequired()], choices=lodgingdata)
    under21_age = IntegerField('If under 21, list age', validators=[])
    onsite_contact_name = StringField('Legal Name', validators=[DataRequired()])
    onsite_contact_sca_name = StringField('SCA Name', validators=[])
    onsite_contact_kingdom = SelectField('Kingdom', validators=[DataRequired()], choices=kingdomdata)
    onsite_contact_group = SelectField('Camping Group', validators=[DataRequired()], choices=lodgingdata)
    offsite_contact_name = StringField('Legal Name', validators=[DataRequired()])
    offsite_contact_phone = StringField('Phone', validators=[DataRequired()])
    rate_age = SelectField('Age Range', validators=[DataRequired()], choices=agedata)
    rate_mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    mbr_num = IntegerField('Membership #', validators=[RequiredIfMembership('rate_mbr')])
    mbr_num_exp = DateField('Exp Date', validators=[RequiredIfMembership('rate_mbr')])
    rate_date = SelectField('Arrival Date', validators=[DataRequired()], choices=arrivaldata)
    submit = SubmitField('Register')

class CheckinForm(FlaskForm):
    regid = IntegerField()
    fname = StringField('First Name')
    lname = StringField('Last Name')
    scaname = StringField('SCA Name')
    kingdom = SelectField('Kingdom', validators=[DataRequired()], choices=kingdomdata)
    lodging = SelectField('Camping Group', validators=[DataRequired()], choices=lodgingdata)
    rate_age = SelectField('Age Range', validators=[DataRequired()], choices=agedata)
    rate_mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    medallion = IntegerField('Medallion #', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditForm(FlaskForm):
    regid = IntegerField()
    fname = StringField('First Name')
    lname = StringField('Last Name')
    scaname = StringField('SCA Name')
    kingdom = SelectField('Kingdom', validators=[DataRequired()], choices=kingdomdata)
    lodging = SelectField('Camping Group', validators=[DataRequired()], choices=lodgingdata)
    rate_age = SelectField('Age Range', validators=[DataRequired()], choices=agedata)
    rate_mbr = SelectField('Membership Status', validators=[DataRequired()], choices=mbrdata)
    medallion = IntegerField('Medallion #', validators=[DataRequired()])
    price_paid = IntegerField('Amount Paid')
    price_calc = IntegerField('Calculated Price')
    price_due = IntegerField('Price Due')

    #mbr_exp
    submit = SubmitField('Submit')

class UpdateInvoiceForm(FlaskForm):
    price_paid = IntegerField('Amount Paid')
    price_calc = IntegerField('Calculated Price')
    price_due = IntegerField('Price Due')
    invoice_number = StringField('Invoice Number', validators=[RequiredIf('invoice_date')])
    invoice_paid = BooleanField('Invoice Paid')
    invoice_date = DateField('Invoice Date', validators=[RequiredIf('invoice_number')])
    invoice_canceled = BooleanField('Invoice Canceled')
    submit = SubmitField('Update Invoice')

class WaiverForm(FlaskForm):
    
    signature = HiddenField(
        'signature',
        render_kw={'id':'signature'}
    )
    
    submit = SubmitField(
        'Submit',
        render_kw={'id':'submit'}
    )

class ReportForm(FlaskForm):
    report_type = SelectField('Report Type', validators=[DataRequired()], choices=reporttypedata)
    dt_start = DateField('Start Date', format='%Y-%m-%d')
    dt_end = DateField('End Date', format='%Y-%m-%d')
    submit = SubmitField('Submit')