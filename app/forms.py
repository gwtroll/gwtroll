from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired
import pandas as pd

lodging_df = pd.read_csv('gwlodging.csv')
lodgingdata = lodging_df.to_dict(orient='list')

kingdom_df = pd.read_csv('gwkingdoms.csv')
kingdomdata = kingdom_df.to_dict(orient='list')

agedata = [('18+', 'Adult 18+'), ('13-17', 'Teen 13 - 17'), ('6-12', 'Youth 6 - 12'), ('0-5', 'Child 0 - 5')]

mbrdata = [('Member', 'Member'), ('Non-Member', 'Non-Member')]

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateRegForm(FlaskForm):
    #regid = HiddenField(None)
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    scaname = StringField('SCA Name', validators=[])
    kingdom = SelectField('Last Name', validators=[DataRequired()], choices=kingdomdata)
    lodging = SelectField('Select an option', validators=[DataRequired()], choices=lodgingdata)
    rate_age = SelectField('Select an option', validators=[DataRequired()], choices=agedata)
    rate_mbr = SelectField('Select an option', validators=[DataRequired()], choices=mbrdata)
    #mbr_num
    #mbr_exp
    submit = SubmitField('Submit')

class CheckinForm(FlaskForm):
    regid = IntegerField()
    fname = StringField('First Name')
    lname = StringField('Last Name')
    scaname = StringField('SCA Name')
    kingdom = SelectField('Last Name', validators=[DataRequired()], choices=kingdomdata)
    lodging = SelectField('Select an option', validators=[DataRequired()], choices=lodgingdata)
    rate_age = SelectField('Select an option', validators=[DataRequired()], choices=agedata)
    rate_mbr = SelectField('Select an option', validators=[DataRequired()], choices=mbrdata)
    medallion = IntegerField('Medallion #', validators=[DataRequired()])
    #mbr_num
    #mbr_exp
    submit = SubmitField('Submit')
