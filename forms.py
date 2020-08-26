from wtforms import Form, BooleanField,IntegerField, StringField, PasswordField, validators, TextAreaField, DecimalField
from flask_wtf.file import FileField, FileAllowed, FileRequired
class RegistrationForm(Form):
    name = StringField('Name',  [validators.Length(min=4, max=25), validators.DataRequired()])
    username = StringField('Username',[validators.Length(min=4, max=25), validators.DataRequired()])
    email = StringField('Email Address',  [validators.Length(min=6, max=35), validators.Email(), validators.DataRequired()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    #accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

class LoginForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email(),  validators.DataRequired()])
    password = PasswordField('New Password', [validators.DataRequired()])

class Addproducts(Form):
    name            = StringField('Name',       [validators.DataRequired()])
    price           = DecimalField('Price',     [validators.DataRequired()])
    discount        = IntegerField('Discount',  [validators.DataRequired()])
    stock           = IntegerField('Stock',     [validators.DataRequired()])
    colors          = TextAreaField('Discription',[validators.DataRequired()])
    image_1         = FileField('Image 1', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg']), 'images only please' ])
    image_2         = FileField('Image 2', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg']), 'images only please'])
    image_3         = FileField('Image 3', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg']), 'images only please'])