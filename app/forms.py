from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, HiddenField, SelectMultipleField
from wtforms.fields import DateField
from wtforms.validators import DataRequired
import pandas as pd

lodging_df = pd.read_csv('gwlodging.csv')
lodgingdata = lodging_df.to_dict(orient='list')

kingdom_df = pd.read_csv('gwkingdoms.csv')
kingdomdata = kingdom_df.to_dict(orient='list')

agedata = [('18+', 'Adult 18+'), ('13-17', 'Teen 13 - 17'), ('6-12', 'Youth 6 - 12'), ('0-5', 'Child 0 - 5'), ('tour_adult', 'Tour 18+'), ('tour_teen', 'Tour 12 - 17'), ('tour_child', 'Tour 0 - 11')]

mbrdata = [('Member', 'Member'), ('Non-Member', 'Non-Member')]

reporttypedata = [('full_export', 'full_export'), ('full_signatue_export', 'full_signature_export'), ('full_checkin_report', 'full_checkin_report'), ('at_door_count', 'at_door_count'), ('kingdom_count', 'kingdom_count'), ('ghost_report', 'ghost_report')]

roledata = [(5, 'User'), (2, 'Shift Lead'), (1, 'Admin'), (3, 'Marshal'),(4, 'Land')]

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
    #mbr_num
    #mbr_exp
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